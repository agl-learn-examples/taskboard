import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:taskboard/api_client.dart';
import 'package:taskboard/token_store.dart';

void main() {
  setUp(() => FlutterSecureStorage.setMockInitialValues({})); // secure storage in memory, for tests

  test('logs in, keeps the tokens, and sends the access token for tasks', () async {
    final requests = <http.Request>[];
    final fakeServer = MockClient((request) async {
      requests.add(request);
      if (request.url.path == '/v1/auth/login') {
        return http.Response(jsonEncode({'access_token': 'A1', 'refresh_token': 'R1'}), 200);
      }
      return http.Response(
          jsonEncode({
            'items': [
              {'id': 1, 'title': 'Pick fonts', 'done': false, 'priority': 'normal', 'board_id': 1}
            ]
          }),
          200);
    });
    final api = ApiClient('http://gateway', TokenStore(), httpClient: fakeServer);

    await api.login('priya@blueleaf.example', 'demo-password-123');
    final tasks = await api.fetchTasks();

    expect(jsonDecode(requests[0].body), {'email': 'priya@blueleaf.example', 'password': 'demo-password-123'});
    expect(requests[1].url.toString(), 'http://gateway/v1/tasks?per_page=100');
    expect(requests[1].headers['Authorization'], 'Bearer A1');
    expect(tasks.single.title, 'Pick fonts');
  });

  test('a wrong password shows the API\'s own message', () async {
    final fakeServer =
        MockClient((request) async => http.Response('{"error": "wrong email or password"}', 401));
    final api = ApiClient('http://gateway', TokenStore(), httpClient: fakeServer);

    expect(
        () => api.login('priya@blueleaf.example', 'nope'),
        throwsA(isA<ApiException>()
            .having((e) => e.message, 'message', 'wrong email or password')
            .having((e) => e.status, 'status', 401)));
  });

  test('logout forgets the tokens', () async {
    FlutterSecureStorage.setMockInitialValues({'access_token': 'A1', 'refresh_token': 'R1'});
    final fakeServer = MockClient((request) async => http.Response('', 204));
    final api = ApiClient('http://gateway', TokenStore(), httpClient: fakeServer);

    expect(await api.isLoggedIn(), true);
    await api.logout();
    expect(await api.isLoggedIn(), false);
  });
}
