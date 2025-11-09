import 'package:flutter/material.dart';

class FitnessScreen extends StatelessWidget {
  static const routeName = '/fitness';

  const FitnessScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Fitness')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          ListTile(title: Text('Executive Vitality'), subtitle: Text('VO2 focus')),
          ListTile(title: Text('Transcend Peak'), subtitle: Text('HRV and strain blend')),
        ],
      ),
    );
  }
}
