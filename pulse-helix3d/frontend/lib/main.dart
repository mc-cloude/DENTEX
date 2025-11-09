import 'package:flutter/material.dart';
import 'routing/app_router.dart';
import 'themes/executive_theme.dart';

void main() {
  runApp(const PulseApp());
}

class PulseApp extends StatelessWidget {
  const PulseApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Pulse HELIX3D',
      theme: buildExecutiveTheme(),
      routerConfig: buildRouter(),
    );
  }
}
