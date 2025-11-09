import 'package:flutter/material.dart';

class NutritionScreen extends StatelessWidget {
  static const routeName = '/nutrition';

  const NutritionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nutrition')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          ListTile(title: Text('Metabolic Reset'), subtitle: Text('1800 kcal, 30/30/40')),
          ListTile(title: Text('Longevity Mediterranean'), subtitle: Text('2100 kcal, 25/35/40')),
        ],
      ),
    );
  }
}
