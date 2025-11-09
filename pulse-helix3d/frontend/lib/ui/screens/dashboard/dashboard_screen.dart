import 'package:flutter/material.dart';

class DashboardScreen extends StatelessWidget {
  static const routeName = '/';

  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Pulse Dashboard')),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        child: const Icon(Icons.bubble_chart),
      ),
      body: GridView.count(
        padding: const EdgeInsets.all(16),
        crossAxisCount: 2,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        children: const [
          _MetricCard(title: 'HRV', value: '72 ms'),
          _MetricCard(title: 'Sleep Debt', value: '1.3 h'),
          _MetricCard(title: 'Strain', value: '0.62'),
          _MetricCard(title: 'Programs', value: 'Transcend Peak'),
        ],
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String title;
  final String value;

  const _MetricCard({required this.title, required this.value});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(title, style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 8),
            Text(value, style: Theme.of(context).textTheme.bodyLarge),
          ],
        ),
      ),
    );
  }
}
