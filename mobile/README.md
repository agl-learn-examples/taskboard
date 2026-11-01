# mobile/ — the TaskBoard phone app (Course A6)

TaskBoard's phone app, built with **Flutter**: one codebase for Android, iOS, the web and desktops. It talks
to the API through the gateway (`/v1/...`), as the web app does. How to install, run and test it: the
section *Course A6: the mobile app* in the [top README](../README.md).

| file | what it does | lesson |
|---|---|---|
| `lib/main.dart` | starts the app; shows the login screen or the task list; `API_BASE` | A6 L2 |
| `lib/screens/task_list_screen.dart` | the task list: loading spinner, the list, "No tasks yet", an error to retry | A6 L2 |
| `lib/widgets/task_row.dart` | one row of the list | A6 L2 |
| `lib/task.dart` | the `Task` model: JSON to a Dart object | A6 L3 |
| `lib/api_client.dart` | `ApiClient`: login, tasks, logout, the token on every request, errors | A6 L3, L4 |
| `lib/token_store.dart` | the tokens in secure storage (Keychain, Keystore) | A6 L4 |
| `lib/screens/login_screen.dart` | the login form | A6 L4 |
| `test/` | unit and widget tests, with a fake API: no server needed | A6 L2–L4 |
| `integration_test/` | the whole app against the running stack | A6 L4 |

`android/`, `ios/`, `linux/` and `web/` are what `flutter create` made, changed only to name the app
TaskBoard, give the Linux window a phone's size, and let Android call a plain-http API on your laptop.
