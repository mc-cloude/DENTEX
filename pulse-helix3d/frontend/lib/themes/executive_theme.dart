import 'package:flutter/material.dart';

ThemeData buildExecutiveTheme() {
  const primaryColor = Color(0xFF0A1F44);
  return ThemeData(
    colorScheme: ColorScheme.fromSeed(seedColor: primaryColor, brightness: Brightness.light),
    scaffoldBackgroundColor: Colors.white,
    textTheme: const TextTheme(
      headlineMedium: TextStyle(fontFamily: 'Roboto', fontWeight: FontWeight.bold, color: primaryColor),
      bodyLarge: TextStyle(fontFamily: 'Roboto', color: primaryColor),
    ),
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      backgroundColor: Color(0xFF1E88E5),
      foregroundColor: Colors.white,
      elevation: 8,
    ),
  );
}
