import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Keeps the login tokens in the phone's secure storage: the Keychain on iOS, the Keystore on Android
/// (the Secret Service keyring on Linux). Never in plain files or SharedPreferences, where other apps
/// or a backup could read them.
class TokenStore {
  final _storage = const FlutterSecureStorage();

  Future<String?> readAccessToken() => _storage.read(key: 'access_token');
  Future<String?> readRefreshToken() => _storage.read(key: 'refresh_token');

  Future<void> save(String accessToken, String refreshToken) async {
    await _storage.write(key: 'access_token', value: accessToken);
    await _storage.write(key: 'refresh_token', value: refreshToken);
  }

  Future<void> clear() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
  }
}
