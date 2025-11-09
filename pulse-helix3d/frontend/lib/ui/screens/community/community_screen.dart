import 'package:flutter/material.dart';

class CommunityScreen extends StatelessWidget {
  static const routeName = '/community';

  const CommunityScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Community')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          ListTile(title: Text('Desert Sunrise HRV'), subtitle: Text('Executive leaderboard')),
          ListTile(title: Text('Corporate Wellness Cup'), subtitle: Text('Tiered recognition')),
        ],
      ),
    );
  }
}
