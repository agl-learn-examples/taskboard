import 'package:flutter/material.dart';

import '../api_client.dart';
import '../task.dart';
import '../widgets/task_row.dart';

/// The team's tasks: a spinner while loading, then the list, "No tasks yet", or an error to retry.
class TaskListScreen extends StatefulWidget {
  const TaskListScreen({super.key, required this.api, required this.onLoggedOut});

  final ApiClient api;
  final VoidCallback onLoggedOut;

  @override
  State<TaskListScreen> createState() => _TaskListScreenState();
}

class _TaskListScreenState extends State<TaskListScreen> {
  List<Task>? _tasks; // null: still loading
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _tasks = null;
      _error = null;
    });
    try {
      final tasks = await widget.api.fetchTasks();
      if (mounted) setState(() => _tasks = tasks);
    } on ApiException catch (e) {
      if (e.status == 401) return _logOut(); // the session is over (logged out elsewhere): log in again
      if (mounted) setState(() => _error = e.message);
    }
  }

  Future<void> _logOut() async {
    await widget.api.logout();
    widget.onLoggedOut();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tasks'),
        actions: [
          IconButton(icon: const Icon(Icons.logout), tooltip: 'Log out', onPressed: _logOut),
        ],
      ),
      body: _body(),
    );
  }

  Widget _body() {
    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(_error!, textAlign: TextAlign.center),
            const SizedBox(height: 16),
            FilledButton(onPressed: _load, child: const Text('Try again')),
          ],
        ),
      );
    }
    final tasks = _tasks;
    if (tasks == null) return const Center(child: CircularProgressIndicator());
    if (tasks.isEmpty) return const Center(child: Text('No tasks yet'));
    return ListView.builder(
      itemCount: tasks.length,
      itemBuilder: (context, index) => TaskRow(task: tasks[index]),
    );
  }
}
