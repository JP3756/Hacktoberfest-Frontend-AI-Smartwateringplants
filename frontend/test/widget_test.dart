import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/main.dart';

void main() {
  testWidgets('dashboard renders greenhouse controls', (WidgetTester tester) async {
    await tester.pumpWidget(const GreenhouseApp());

    expect(find.text('Current Conditions'), findsOneWidget);
    expect(find.text('Water Usage History'), findsOneWidget);
    expect(find.text('Water Pump #1'), findsOneWidget);
    expect(find.text('Pump #1 Overheating'), findsOneWidget);
  });
}
