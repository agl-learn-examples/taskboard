import 'package:flutter/material.dart';

import 'api_client.dart';
import 'screens/login_screen.dart';
import 'screens/task_list_screen.dart';
import 'token_store.dart';

/// The gateway's address. Change it when you start the app:
///   flutter run --dart-define=API_BASE=http://10.0.2.2:8080     (the Android emulator's name for your laptop)
const apiBase = String.fromEnvironment('API_BASE', defaultValue: 'http://localhost:8080');

void main() {
  runApp(TaskBoardApp(api: ApiClient(apiBase, TokenStore())));
}

/// The whole app: the login screen, or the task list once logged in.
class TaskBoardApp extends StatefulWidget {
  const TaskBoardApp({super.key, required this.api});

  final ApiClient api;

  @override
  State<TaskBoardApp> createState() => _TaskBoardAppState();
}

class _TaskBoardAppState extends State<TaskBoardApp> {
  bool? _loggedIn; // null: still looking for a saved token

  @override
  void initState() {
    super.initState();
    widget.api.isLoggedIn().then((loggedIn) => setState(() => _loggedIn = loggedIn));
  }

  @override
  Widget build(BuildContext context) {
    final Widget home;
    if (_loggedIn == null) {
      home = const Scaffold(body: Center(child: CircularProgressIndicator()));
    } else if (_loggedIn!) {
      home = TaskListScreen(api: widget.api, onLoggedOut: () => setState(() => _loggedIn = false));
    } else {
      home = LoginScreen(api: widget.api, onLoggedIn: () => setState(() => _loggedIn = true));
    }
    return MaterialApp(
      title: 'TaskBoard',
      theme: ThemeData(colorSchemeSeed: Colors.indigo),
      home: home,
    );
  }
}
