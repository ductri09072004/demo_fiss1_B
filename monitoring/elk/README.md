# ELK Stack for Demo FISS1

## 🎯 **Mục đích:**
- **Elasticsearch**: Lưu trữ và tìm kiếm logs
- **Logstash**: Xử lý và parse logs
- **Kibana**: Visualization và dashboard
- **Filebeat**: Thu thập logs từ Docker containers

## 🚀 **Cách sử dụng:**

### **1. Khởi động ELK Stack:**
```powershell
cd monitoring\elk
.\start-elk.ps1
```

### **2. Truy cập Kibana:**
- **URL**: http://localhost:5601
- **Tạo Index Pattern**: `demo-fiss-logs-*`
- **Time Field**: `@timestamp`

### **3. Xem logs:**
- **Discover**: Xem logs thô
- **Dashboard**: Biểu đồ logs
- **Search**: Tìm kiếm logs

## 📊 **Logs được thu thập:**
- **Flask API logs**: Requests, responses, errors
- **Docker container logs**: System logs
- **Application logs**: Custom application logs

## 🔧 **Cấu hình:**
- **Elasticsearch**: Port 9200
- **Kibana**: Port 5601
- **Logstash**: Port 5044, 5000
- **Filebeat**: Thu thập từ Docker

## 📈 **Dashboard có sẵn:**
- **API Requests Over Time**: Số lượng requests theo thời gian
- **Error Rate**: Tỷ lệ lỗi
- **Response Time**: Thời gian phản hồi
- **Log Analysis**: Phân tích logs chi tiết

## 🎯 **Lợi ích:**
- **Centralized Logging**: Tập trung logs
- **Real-time Monitoring**: Giám sát thời gian thực
- **Search & Analysis**: Tìm kiếm và phân tích
- **Alerting**: Cảnh báo khi có lỗi
