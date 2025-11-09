import 'package:flutter/material.dart';

class RecoveryScreen extends StatelessWidget {
  static const routeName = '/recovery';

  const RecoveryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Recovery')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          ListTile(title: Text('Sleep Debt'), subtitle: Text('1.3 hours')),
          ListTile(title: Text('HRV Trend'), subtitle: Text('72 → 74 ms')),
        ],
      ),
    );
  }
}
