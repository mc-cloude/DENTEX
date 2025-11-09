import 'package:flutter/material.dart';
import '../ui/screens/dashboard/dashboard_screen.dart';
import '../ui/screens/onboarding/onboarding_screen.dart';
import '../ui/screens/nutrition/nutrition_screen.dart';
import '../ui/screens/fitness/fitness_screen.dart';
import '../ui/screens/recovery/recovery_screen.dart';
import '../ui/screens/community/community_screen.dart';
import '../ui/screens/profile/profile_screen.dart';

RouterConfig<Object> buildRouter() {
  return RouterConfig(
    navigatorKey: GlobalKey<NavigatorState>(),
    onGenerateRoute: (settings) {
      Widget page = const DashboardScreen();
      switch (settings.name) {
        case OnboardingScreen.routeName:
          page = const OnboardingScreen();
          break;
        case NutritionScreen.routeName:
          page = const NutritionScreen();
          break;
        case FitnessScreen.routeName:
          page = const FitnessScreen();
          break;
        case RecoveryScreen.routeName:
          page = const RecoveryScreen();
          break;
        case CommunityScreen.routeName:
          page = const CommunityScreen();
          break;
        case ProfileScreen.routeName:
          page = const ProfileScreen();
          break;
      }
      return MaterialPageRoute(builder: (_) => page, settings: settings);
    },
  );
}
