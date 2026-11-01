import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:taskboard/api_client.dart';
import 'package:taskboard/screens/task_list_screen.dart';
import 'package:taskboard/task.dart';
import 'package:taskboard/token_store.dart';

/// A pretend ApiClient: fetchTasks answers whatever the test puts in [answer], with no network.
class FakeApiClient extends ApiClient {
  FakeApiClient() : super('http://fake', TokenStore());

  Completer<List<Task>> answer = Completer();

  @override
  Future<List<Task>> fetchTasks() => answer.future;
}

Widget screenWith(ApiClient api) =>
    MaterialApp(home: TaskListScreen(api: api, onLoggedOut: () {}));

void main() {
  testWidgets('shows a spinner, then the tasks', (tester) async {
    final api = FakeApiClient();
    await tester.pumpWidget(screenWith(api));
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    api.answer.complete(const [
      Task(id: 1, title: 'Draw the home page', done: false, priority: 'high'),
      Task(id: 2, title: 'Pick fonts', done: true, priority: 'normal'),
    ]);
    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsNothing);
    expect(find.text('Draw the home page'), findsOneWidget);
    expect(find.text('Pick fonts'), findsOneWidget);
    expect(find.byIcon(Icons.check_circle), findsOneWidget); // only "Pick fonts" is done
  });

  testWidgets('says so when there are no tasks', (tester) async {
    final api = FakeApiClient();
    await tester.pumpWidget(screenWith(api));
    api.answer.complete([]);
    await tester.pump();

    expect(find.text('No tasks yet'), findsOneWidget);
  });

  testWidgets('shows the error and tries again', (tester) async {
    final api = FakeApiClient();
    await tester.pumpWidget(screenWith(api));
    api.answer.completeError(ApiException('Cannot reach TaskBoard'));
    await tester.pump();
    expect(find.text('Cannot reach TaskBoard'), findsOneWidget);

    api.answer = Completer()..complete([const Task(id: 1, title: 'Pick fonts', done: false, priority: 'low')]);
    await tester.tap(find.text('Try again'));
    await tester.pump();

    expect(find.text('Pick fonts'), findsOneWidget);
  });
}
