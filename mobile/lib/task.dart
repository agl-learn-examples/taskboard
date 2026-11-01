/// One task, as the API sends it:
/// {"id": 1, "title": "Pick fonts", "done": false, "priority": "normal", "board_id": 1}
class Task {
  const Task({
    required this.id,
    required this.title,
    required this.done,
    required this.priority,
    this.boardId,
  });

  final int id;
  final String title;
  final bool done;
  final String priority; // "low", "normal" or "high"
  final int? boardId; // null: the task is on no board

  /// JSON (a Map) to a Task. A missing or wrong-typed field throws a TypeError:
  /// better to fail here than to show half a task.
  factory Task.fromJson(Map<String, dynamic> json) {
    return Task(
      id: json['id'] as int,
      title: json['title'] as String,
      done: json['done'] as bool,
      priority: json['priority'] as String,
      boardId: json['board_id'] as int?,
    );
  }
}
