# Proje açıklaması - Türkçe

**Huawei Cloud FinOps & Akıllı Kapasite Optimizasyon Platformu**

Huawei Cloud maliyet, kullanım, sahiplik ve kapasite verilerini öncelikli ve
açıklanabilir mühendislik kararlarına dönüştüren uçtan uca bir FinOps platformu
tasarlandı ve geliştirildi. Çözüm; maliyet dağıtımı, bütçe yönetimi, robust
anomali tespiti, aylık tahminleme, ECS/RDS/CCE rightsizing, Kubernetes request
verimliliği, atıl kaynak tespiti, OBS yaşam döngüsü fırsatları, satın alma modeli
adayları ve kapasite risk kontrollerini kapsıyor.

Altı aylık deterministik veri seti tüm akışı tekrarlanabilir hâle getiriyor.
Demo portföyünde 6.133,36 USD aylık amortize maliyet analiz edilerek çift
sayım yapılmadan 1.520,70 USD aylık ve 18.248,40 USD yıllıklandırılmış tasarruf
fırsatı belirlendi. Maliyet dağıtım kapsamı %97,43, bütçe kapsamı ise %100 olarak
ölçüldü.

Platformda Python analitik motoru, FastAPI, CLI, Docker Compose kontrol kulesi,
Prometheus metrikleri, Grafana dashboard, güvenli Kubernetes manifestleri,
Kustomize dev/prod ortamları, parametrik Helm chart ve Huawei Cloud CCE, OBS,
SMN için Terraform modülleri bulunuyor. OPA/Rego politikaları maliyet etiketleri,
CPU/bellek istekleri, güvenli konteyner çalıştırma ve kapasite sınırlarını
uygulanabilir kurallara dönüştürüyor. GitHub Actions; Python 3.11/3.12 testleri,
%90 coverage kapısı, veri drift kontrolü, Terraform doğrulaması, container smoke
testi, CodeQL ve Trivy güvenlik taramalarını otomatikleştiriyor.

Servis bilinçli şekilde read-only tasarlandı. Her öneri kanıt, risk, güven,
tahmini tasarruf ve geri döndürülebilir aksiyon içerirken üretim uygulaması
kaynak sahibi onayının arkasında tutuluyor.

**Teknolojiler:** Huawei Cloud Cost Center, CCE, AOM, Cloud Eye, OBS, SMN, SWR,
Python, FastAPI, Docker, Kubernetes, Kustomize, Helm, Terraform, OPA/Rego,
Prometheus, Grafana, GitHub Actions, CodeQL, Trivy, Ruff, Pytest.
