import 'package:flutter_test/flutter_test.dart';
import 'package:taskboard/task.dart';

void main() {
  test('reads a task from the API JSON', () {
    final task = Task.fromJson(
        {'id': 1, 'title': 'Pick fonts', 'done': false, 'priority': 'normal', 'board_id': 3});

    expect(task.id, 1);
    expect(task.title, 'Pick fonts');
    expect(task.done, false);
    expect(task.priority, 'normal');
    expect(task.boardId, 3);
  });

  test('a task on no board has board_id null', () {
    final task =
        Task.fromJson({'id': 2, 'title': 'Order stock', 'done': true, 'priority': 'high', 'board_id': null});

    expect(task.boardId, isNull);
    expect(task.done, true);
  });

  test('a task without a title is refused', () {
    expect(() => Task.fromJson({'id': 3, 'done': false, 'priority': 'low'}), throwsA(isA<TypeError>()));
  });
}
