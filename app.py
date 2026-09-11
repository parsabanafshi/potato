import os
import requests
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ================================================
# 🧪 تست یک پروکسی
# ================================================
def test_proxy(proxy_url, test_url="https://tapi.bale.ai", timeout=10):
    """
    تست پروکسی با اتصال به یه URL خاص
    """
    result = {
        "proxy": proxy_url,
        "success": False,
        "status_code": None,
        "response_time": None,
        "error": None,
        "ip_info": None
    }
    
    try:
        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }
        
        start_time = time.time()
        
        response = requests.get(
            test_url,
            proxies=proxies,
            timeout=timeout,
            allow_redirects=False
        )
        
        elapsed = time.time() - start_time
        
        result["success"] = True
        result["status_code"] = response.status_code
        result["response_time"] = round(elapsed, 2)
        
        # تست IP خارجی
        try:
            ip_response = requests.get(
                "https://api.ipify.org?format=json",
                proxies=proxies,
                timeout=10
            )
            if ip_response.status_code == 200:
                result["ip_info"] = ip_response.json().get("ip")
        except:
            pass
        
    except requests.exceptions.ProxyError as e:
        result["error"] = f"Proxy Error: {str(e)[:100]}"
    except requests.exceptions.ConnectTimeout:
        result["error"] = "Connection Timeout"
    except requests.exceptions.ReadTimeout:
        result["error"] = "Read Timeout"
    except requests.exceptions.SSLError as e:
        result["error"] = f"SSL Error: {str(e)[:100]}"
    except Exception as e:
        result["error"] = f"Error: {str(e)[:100]}"
    
    return result


# ================================================
# 🌐 صفحه اصلی
# ================================================
PAGE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧪 پروکسی تستر</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: Tahoma, Arial, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            text-align: center;
            color: #aaa;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        textarea {
            width: 100%;
            min-height: 150px;
            padding: 15px;
            background: #0e0f12;
            color: #fff;
            border: 1px solid #333;
            border-radius: 10px;
            font-family: monospace;
            font-size: 14px;
            direction: ltr;
            resize: vertical;
        }
        .row {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        input[type="text"] {
            flex: 1;
            min-width: 250px;
            padding: 12px;
            background: #0e0f12;
            color: #fff;
            border: 1px solid #333;
            border-radius: 10px;
            direction: ltr;
        }
        button {
            padding: 12px 30px;
            border: 0;
            border-radius: 10px;
            background: #5865f2;
            color: #fff;
            cursor: pointer;
            font-size: 15px;
            font-weight: bold;
            transition: 0.3s;
        }
        button:hover {
            background: #4752c4;
            transform: scale(1.03);
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .results {
            margin-top: 20px;
        }
        .result-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            background: rgba(255,255,255,0.03);
            border-left: 4px solid #555;
            direction: ltr;
        }
        .result-item.success {
            border-left-color: #00c853;
            background: rgba(0, 200, 83, 0.1);
        }
        .result-item.failed {
            border-left-color: #d50000;
            background: rgba(213, 0, 0, 0.05);
        }
        .result-item .proxy {
            flex: 1;
            font-family: monospace;
            font-size: 13px;
            word-break: break-all;
        }
        .result-item .status {
            font-size: 20px;
            min-width: 30px;
            text-align: center;
        }
        .result-item .time {
            font-size: 13px;
            color: #aaa;
            min-width: 70px;
        }
        .result-item .error {
            font-size: 12px;
            color: #ff5252;
            max-width: 200px;
        }
        .ip-info {
            font-size: 11px;
            color: #64b5f6;
            max-width: 150px;
            word-break: break-all;
        }
        .summary {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .stat {
            flex: 1;
            min-width: 120px;
            padding: 15px;
            border-radius: 10px;
            background: rgba(255,255,255,0.05);
            text-align: center;
        }
        .stat .number {
            font-size: 28px;
            font-weight: bold;
        }
        .stat .label {
            font-size: 12px;
            color: #aaa;
            margin-top: 5px;
        }
        .stat.green .number { color: #00c853; }
        .stat.red .number { color: #d50000; }
        .stat.blue .number { color: #64b5f6; }
        .loading {
            text-align: center;
            padding: 20px;
            color: #aaa;
            display: none;
        }
        .loading.active { display: block; }
        .default-proxies {
            font-size: 12px;
            color: #888;
            margin-top: 10px;
            cursor: pointer;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 پروکسی تستر</h1>
        <p class="subtitle">پروکسی‌ها را از Railway تست کنید</p>

        <div class="card">
            <label style="display:block;margin-bottom:10px;color:#aaa;">
                لیست پروکسی‌ها (هر خط یکی):
            </label>
            <textarea id="proxyList" placeholder="socks5://93.118.127.222:1080&#10;socks5://185.142.156.229:2080">socks5://93.118.127.222:1080
socks5://185.142.156.229:2080
socks5://178.252.180.59:10909
socks5://85.133.190.40:8097
socks5://91.228.133.191:9999</textarea>

            <div class="row">
                <input type="text" id="testUrl" value="https://tapi.bale.ai" placeholder="URL تست">
                <input type="text" id="timeout" value="10" placeholder="Timeout" style="max-width:100px;">
                <button id="testBtn" onclick="testProxies()">🚀 شروع تست</button>
            </div>
            <p class="default-proxies" onclick="loadDefaults()">بارگذاری پروکسی‌های پیش‌فرض</p>
        </div>

        <div class="loading" id="loading">
            ⏳ در حال تست پروکسی‌ها... لطفاً صبر کنید
        </div>

        <div class="summary" id="summary" style="display:none;">
            <div class="stat green">
                <div class="number" id="successCount">0</div>
                <div class="label">موفق ✅</div>
            </div>
            <div class="stat red">
                <div class="number" id="failCount">0</div>
                <div class="label">ناموفق ❌</div>
            </div>
            <div class="stat blue">
                <div class="number" id="totalCount">0</div>
                <div class="label">کل</div>
            </div>
        </div>

        <div class="results" id="results"></div>
    </div>

    <script>
        function loadDefaults() {
            document.getElementById('proxyList').value = `socks5://93.118.127.222:1080
socks5://185.142.156.229:2080
socks5://178.252.180.59:10909
socks5://85.133.190.40:8097
socks5://91.228.133.191:9999`;
        }

        async function testProxies() {
            const proxyList = document.getElementById('proxyList').value
                .split('\\n')
                .map(p => p.trim())
                .filter(p => p);

            if (proxyList.length === 0) {
                alert('لطفاً حداقل یک پروکسی وارد کنید');
                return;
            }

            const testUrl = document.getElementById('testUrl').value;
            const timeout = parseInt(document.getElementById('timeout').value) || 10;

            document.getElementById('testBtn').disabled = true;
            document.getElementById('loading').classList.add('active');
            document.getElementById('results').innerHTML = '';
            document.getElementById('summary').style.display = 'none';

            try {
                const response = await fetch('/test', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        proxies: proxyList,
                        test_url: testUrl,
                        timeout: timeout
                    })
                });

                const data = await response.json();
                displayResults(data.results);
            } catch (e) {
                alert('خطا: ' + e.message);
            } finally {
                document.getElementById('testBtn').disabled = false;
                document.getElementById('loading').classList.remove('active');
            }
        }

        function displayResults(results) {
            const container = document.getElementById('results');
            let success = 0, fail = 0;

            results.forEach(r => {
                const div = document.createElement('div');
                div.className = 'result-item ' + (r.success ? 'success' : 'failed');

                let html = `
                    <div class="status">${r.success ? '✅' : '❌'}</div>
                    <div class="proxy">${r.proxy}</div>
                `;

                if (r.success) {
                    success++;
                    html += `
                        <div class="time">${r.response_time}s</div>
                        <div class="time">HTTP ${r.status_code}</div>
                    `;
                    if (r.ip_info) {
                        html += `<div class="ip-info">🌐 ${r.ip_info}</div>`;
                    }
                } else {
                    fail++;
                    html += `<div class="error">${r.error || 'Unknown'}</div>`;
                }

                div.innerHTML = html;
                container.appendChild(div);
            });

            document.getElementById('successCount').textContent = success;
            document.getElementById('failCount').textContent = fail;
            document.getElementById('totalCount').textContent = results.length;
            document.getElementById('summary').style.display = 'flex';
        }
    </script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(PAGE)


@app.route("/test", methods=["POST"])
def test():
    data = request.json
    proxies = data.get("proxies", [])
    test_url = data.get("test_url", "https://tapi.bale.ai")
    timeout = data.get("timeout", 10)
    
    if not proxies:
        return jsonify({"error": "پروکسی وارد نشده"}), 400
    
    results = []
    
    # تست همزمان با thread
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(test_proxy, proxy, test_url, timeout): proxy
            for proxy in proxies
        }
        
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    "proxy": futures[future],
                    "success": False,
                    "error": str(e)
                })
    
    # مرتب‌سازی: موفق‌ها اول
    results.sort(key=lambda x: (not x["success"], x.get("response_time", 999)))
    
    return jsonify({"results": results})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    
    print("=" * 55)
    print("🧪 پروکسی تستر - Railway")
    print(f"🌐 Listening on port {port}")
    print("=" * 55)
    
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
