import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiClient {
  ApiClient(this.baseUrl, {this.token});

  final String baseUrl;
  final String? token;

  Future<Map<String, dynamic>> get(String path) async {
    final response = await http.get(Uri.parse('$baseUrl$path'), headers: _headers());
    return _decode(response);
  }

  Future<Map<String, dynamic>> post(String path, Map<String, dynamic> body) async {
    final response = await http.post(Uri.parse('$baseUrl$path'), headers: _headers(), body: jsonEncode(body));
    return _decode(response);
  }

  Map<String, String> _headers() {
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Map<String, dynamic> _decode(http.Response response) {
    if (response.statusCode >= 400) {
      throw Exception('Request failed: ${response.statusCode}');
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }
}
