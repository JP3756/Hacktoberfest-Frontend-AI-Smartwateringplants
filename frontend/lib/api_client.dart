import 'dart:convert';

import 'package:http/http.dart' as http;

class SensorReading {
  const SensorReading({required this.moisture, required this.waterLevel});

  final int moisture;
  final int waterLevel;

  factory SensorReading.fromJson(Map<String, dynamic> json) => SensorReading(
        moisture: (json['moisture_level'] as num?)?.toInt() ?? 0,
        waterLevel: (json['water_level'] as num?)?.toInt() ?? 0,
      );
}

class PumpInfo {
  const PumpInfo({required this.id, required this.mode});

  final int id;
  final int? mode;

  factory PumpInfo.fromJson(Map<String, dynamic> json) => PumpInfo(
        id: (json['id'] as num).toInt(),
        mode: (json['mode'] as num?)?.toInt(),
      );
}

class GreenhouseSnapshot {
  const GreenhouseSnapshot({required this.sensor, required this.pumps});

  final SensorReading? sensor;
  final List<PumpInfo> pumps;
}

class GreenhouseApi {
  GreenhouseApi({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  String get baseUrl => const String.fromEnvironment(
        'API_BASE_URL',
        defaultValue: 'http://localhost:8000',
      );

  Future<GreenhouseSnapshot> loadSnapshot() async {
    final responses = await Future.wait([
      _get('/sensor-data/'),
      _get('/pump/'),
      _get('/pump-mode/'),
    ]);
    final sensors = (responses[0] as List)
        .whereType<Map<String, dynamic>>()
        .map(SensorReading.fromJson)
        .toList();
    final pumps = (responses[1] as List)
        .whereType<Map<String, dynamic>>()
        .map((json) => PumpInfo(id: (json['id'] as num).toInt(), mode: null))
        .toList();
    final modes = (responses[2] as List).whereType<Map<String, dynamic>>();
    final modeByPump = {
      for (final mode in modes)
        (mode['pump_id'] as num).toInt(): (mode['mode'] as num).toInt(),
    };

    return GreenhouseSnapshot(
      sensor: sensors.isEmpty ? null : sensors.last,
      pumps: pumps
          .map((pump) => PumpInfo(id: pump.id, mode: modeByPump[pump.id]))
          .toList(),
    );
  }

  Future<void> updatePumpMode(int pump, int pumpMode) async {
    await _request(
      '/pump-mode/',
      method: 'PUT',
      body: {'pump': pump, 'pump_mode': pumpMode},
    );
  }

  Future<dynamic> _get(String path) async {
    final response = await _client
        .get(Uri.parse('$baseUrl$path'))
        .timeout(const Duration(seconds: 3));
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('GET $path failed: ${response.statusCode}');
    }
    return jsonDecode(response.body);
  }

  Future<void> _request(
    String path, {
    required String method,
    required Map<String, dynamic> body,
  }) async {
    final uri = Uri.parse('$baseUrl$path');
    final response = method == 'PUT'
        ? await _client
            .put(uri, headers: {'Content-Type': 'application/json'}, body: jsonEncode(body))
            .timeout(const Duration(seconds: 3))
        : throw UnsupportedError(method);
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('$method $path failed: ${response.statusCode}');
    }
  }

  void dispose() => _client.close();
}
