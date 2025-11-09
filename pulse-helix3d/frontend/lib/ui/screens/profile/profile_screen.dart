import 'package:flutter/material.dart';

class ProfileScreen extends StatelessWidget {
  static const routeName = '/profile';

  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          ListTile(title: Text('Tier'), subtitle: Text('Transcend')),
          ListTile(title: Text('Data Export'), subtitle: Text('Available via dashboard')), 
          ListTile(title: Text('Right to Erasure'), subtitle: Text('Trigger DSR workflow')), 
        ],
      ),
    );
  }
}
