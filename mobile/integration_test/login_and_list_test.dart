// The whole app against the real stack: log in as Priya, see her team's tasks, log out.
//   docker compose up -d --build --wait          (in the repo's top folder)
//   flutter test integration_test -d linux       (in mobile/)
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:taskboard/api_client.dart';
import 'package:taskboard/main.dart';
import 'package:taskboard/token_store.dart';

/// Pumps frames until [finder] finds something: real network calls take real time.
Future<void> waitFor(WidgetTester tester, Finder finder) async {
  for (var i = 0; i < 100 && finder.evaluate().isEmpty; i++) {
    await tester.pump(const Duration(milliseconds: 100));
  }
  expect(finder, findsWidgets);
}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('log in, list tasks, log out', (tester) async {
    await TokenStore().clear(); // start logged out
    await tester.pumpWidget(TaskBoardApp(api: ApiClient(apiBase, TokenStore())));

    await waitFor(tester, find.byKey(const Key('email')));
    await tester.enterText(find.byKey(const Key('email')), 'priya@blueleaf.example');
    await tester.enterText(find.byKey(const Key('password')), 'demo-password-123');
    await tester.tap(find.byKey(const Key('login')));

    await waitFor(tester, find.text('Draw the home page'));
    expect(find.text('Order stock'), findsNothing); // Sharma Traders' task: another tenant

    await tester.tap(find.byTooltip('Log out'));
    await waitFor(tester, find.byKey(const Key('login')));
    expect(await TokenStore().readAccessToken(), isNull);
  });
}
