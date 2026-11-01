import 'dart:convert';

import 'package:http/http.dart' as http;

import 'task.dart';
import 'token_store.dart';

/// Something went wrong talking to TaskBoard. [message] is fit to show the user.
class ApiException implements Exception {
  ApiException(this.message, {this.status});

  final String message;
  final int? status; // the HTTP status, or null if the server could not be reached

  @override
  String toString() => message;
}

/// Talks to TaskBoard's API through the gateway, as the web app does: every path starts with /v1.
class ApiClient {
  ApiClient(this.baseUrl, this.tokens, {http.Client? httpClient})
      : _http = httpClient ?? http.Client();

  final String baseUrl; // e.g. http://localhost:8080
  final TokenStore tokens;
  final http.Client _http;

  Future<bool> isLoggedIn() async => await tokens.readAccessToken() != null;

  /// POST /v1/auth/login, then keep both tokens in secure storage.
  Future<void> login(String email, String password) async {
    final body = await _send('POST', '/v1/auth/login',
        body: {'email': email, 'password': password}, withToken: false);
    await tokens.save(body['access_token'], body['refresh_token']);
  }

  /// GET /v1/tasks: the first 100 of this tenant's tasks.
  Future<List<Task>> fetchTasks() async {
    final body = await _send('GET', '/v1/tasks?per_page=100');
    final items = body['items'] as List;
    return items.map((item) => Task.fromJson(item)).toList();
  }

  /// POST /v1/auth/logout ends the session on the server; then forget the tokens on the phone.
  Future<void> logout() async {
    try {
      await _send('POST', '/v1/auth/logout',
          body: {'refresh_token': await tokens.readRefreshToken()}, retry: false);
    } on ApiException {
      // the server could not be told (offline, or already logged out): forget the tokens anyway
    }
    await tokens.clear();
  }

  /// Sends one request and returns the JSON answer. Adds `Authorization: Bearer <access token>` unless
  /// [withToken] is false. On 401 (the access token expired, after 15 minutes) it gets a new token pair
  /// with the refresh token and tries once more.
  Future<Map<String, dynamic>> _send(String method, String path,
      {Map<String, dynamic>? body, bool withToken = true, bool retry = true}) async {
    final request = http.Request(method, Uri.parse('$baseUrl$path'));
    request.headers['Content-Type'] = 'application/json';
    if (withToken) {
      request.headers['Authorization'] = 'Bearer ${await tokens.readAccessToken()}';
    }
    if (body != null) request.body = jsonEncode(body);

    final http.Response response;
    try {
      response = await http.Response.fromStream(await _http.send(request));
    } on http.ClientException {
      throw ApiException('Cannot reach TaskBoard at $baseUrl. Is it running?');
    }

    if (response.statusCode == 401 && withToken && retry && await _refreshTokens()) {
      return _send(method, path, body: body, retry: false);
    }
    if (response.statusCode >= 400) {
      throw ApiException(_errorMessage(response), status: response.statusCode);
    }
    return response.body.isEmpty ? {} : jsonDecode(response.body);
  }

  /// POST /v1/auth/refresh: swaps the refresh token for a new pair. False if that did not work.
  Future<bool> _refreshTokens() async {
    final refreshToken = await tokens.readRefreshToken();
    if (refreshToken == null) return false;
    try {
      final body = await _send('POST', '/v1/auth/refresh',
          body: {'refresh_token': refreshToken}, withToken: false);
      await tokens.save(body['access_token'], body['refresh_token']);
      return true;
    } on ApiException {
      return false;
    }
  }

  /// TaskBoard's errors are JSON: {"error": "wrong email or password"}.
  String _errorMessage(http.Response response) {
    try {
      return jsonDecode(response.body)['error'] as String;
    } catch (_) {
      return 'Something went wrong (HTTP ${response.statusCode})';
    }
  }
}
