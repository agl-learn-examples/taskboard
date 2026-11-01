import 'package:flutter/material.dart';

import '../task.dart';

/// One line of the task list: done or not, the title, and the priority.
class TaskRow extends StatelessWidget {
  const TaskRow({super.key, required this.task});

  final Task task;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return ListTile(
      leading: Icon(
        task.done ? Icons.check_circle : Icons.radio_button_unchecked,
        color: task.done ? colors.primary : colors.outline,
      ),
      title: Text(
        task.title,
        style: task.done ? const TextStyle(decoration: TextDecoration.lineThrough) : null,
      ),
      trailing: Text(
        task.priority,
        style: TextStyle(color: task.priority == 'high' ? colors.error : colors.outline),
      ),
    );
  }
}
