"""Tests for aionep data models."""

from __future__ import annotations

from aionep.models import (
    AlertInfo,
    AuthData,
    ChartData,
    DateStatistics,
    Device,
    DeviceDetail,
    DeviceModules,
    DeviceStatisticsOverview,
    EnergyFlow,
    EnvironmentalBenefit,
    Module,
    OverviewData,
    PlaybackData,
    PlaybackModule,
    PowerParameter,
    ProductionStatistics,
    Site,
    SiteDetail,
    SiteModulesData,
    SiteOverview,
    SiteStatusCounts,
    Weather,
    WeatherDay,
)


class TestAuthData:
    def test_from_dict(self) -> None:
        raw = {
            "userInfo": {
                "uid": "uid_123",
                "email": "test@example.com",
                "country": "US",
                "state": "CA",
                "role": 0,
                "groupId": 1,
                "groupName": "End User",
                "headerImg": "",
                "defaultArea": "NA",
                "companyId": 0,
                "isCompanyOwner": 0,
                "oemid": 0,
                "oemweb": "NEP",
            },
            "tokenInfo": {
                "token": "jwt_token",
                "expiresAt": 9999999999,
                "duration": 43200,
            },
            "siteCount": 2,
        }
        auth = AuthData.from_dict(raw)
        assert auth.user_info.uid == "uid_123"
        assert auth.user_info.email == "test@example.com"
        assert auth.token_info.token == "jwt_token"
        assert auth.token_info.expires_at == 9999999999
        assert auth.site_count == 2


class TestDevice:
    def test_from_dict(self) -> None:
        raw = {
            "sid": "SITE_1",
            "sn": "AABB1122",
            "status": 0,
            "statusTitle": "online",
            "alertCode": "0000",
            "alertTitle": "OK",
            "alertDescription": "ok",
            "model": 11,
            "modelName": "BDM-2250",
            "lastUpdateTime": 1700000000,
            "lastUpdate": "01/01/2026 12:00",
            "lastUpdateCal": "Just now",
            "createdAt": "01/01/2026 00:00",
            "siteName": "Test Site",
            "country": "US",
            "countryName": "United States",
            "stateName": "California",
            "city": "LA",
            "street": "123 St",
            "userEmail": "test@example.com",
            "installerEmail": "inst@example.com",
            "commissionDate": "",
            "now": 1500,
            "nowUnit": "W",
            "batterySoc": 0,
            "WIFIVersion": "3.01.25",
            "CPUVersion": "",
            "RAMVersion": "",
            "alias": "",
        }
        device = Device.from_dict(raw)
        assert device.sn == "AABB1122"
        assert device.model_name == "BDM-2250"
        assert device.now == 1500
        assert device.is_online is True

    def test_offline(self) -> None:
        device = Device.from_dict({"status": -1, "statusTitle": "offline"})
        assert device.is_online is False


class TestSite:
    def test_from_dict(self) -> None:
        raw = {
            "sid": "SITE_1",
            "siteName": "My Site",
            "country": "US",
            "countryName": "United States",
            "stateName": "CA",
            "city": "LA",
            "street": "123 St",
            "userEmail": "u@e.com",
            "installerEmail": "i@e.com",
            "registerDate": "01/01/2026",
            "isCommission": False,
            "commissionDate": "",
            "snCount": 1,
            "sn": [
                {
                    "sid": "SITE_1",
                    "sn": "AAA",
                    "model": "BDM-2250",
                    "status": 0,
                    "statusTitle": "online",
                    "alertCode": "0000",
                    "alertTitle": "OK",
                    "alertDescription": "ok",
                    "lastUpdate": "",
                    "lastUpdateCal": "",
                    "lastUpdateTime": 0,
                    "now": 500,
                    "todayPower": 2.0,
                    "totalPower": 100,
                    "nowUnit": "W",
                    "todayPowerUnit": "kWh",
                    "totalPowerUnit": "kWh",
                }
            ],
            "status": 0,
            "statusTitle": "online",
            "logo": "",
            "now": 500,
            "todayPower": 2.0,
            "totalPower": 100,
            "nowUnit": "W",
            "todayPowerUnit": "kWh",
            "totalPowerUnit": "kWh",
            "lastUpdate": "",
            "lastUpdateCal": "",
            "lastUpdateTime": 0,
        }
        site = Site.from_dict(raw)
        assert site.sid == "SITE_1"
        assert site.site_name == "My Site"
        assert len(site.devices) == 1
        assert site.devices[0].sn == "AAA"
        assert site.is_online is True


class TestModule:
    def test_from_dict(self) -> None:
        raw = {
            "plcSN": "AABB1122_1",
            "addr": 1,
            "lastUpdate": "2026-01-01 12:00",
            "lastUpdateTime": 1700000000,
            "now": 400,
            "todayPower": 1.5,
            "totalPower": 50,
            "nowUnit": "W",
            "todayPowerUnit": "kWh",
            "totalPowerUnit": "kWh",
            "version": "v1",
            "status": "0000",
            "page": 0,
            "model": 0,
            "model_name": "-",
        }
        mod = Module.from_dict(raw)
        assert mod.plc_sn == "AABB1122_1"
        assert mod.now == 400
        assert mod.total_power == 50


class TestEnergyFlow:
    def test_from_dict(self) -> None:
        raw = {
            "PVPanel": {"power": 1000, "powerUnit": "W", "direction": 1, "show": True, "rate": 0, "showPower": True},
            "home": {"power": 1000, "powerUnit": "W", "direction": 2, "show": True, "rate": 0, "showPower": False},
            "grid": {"power": 0, "powerUnit": "W", "direction": 0, "show": True, "rate": 0, "showPower": False},
            "battery": {"power": 0, "powerUnit": "W", "direction": 0, "show": False, "rate": 0, "showPower": False},
            "gen": {"power": 0, "powerUnit": "W", "direction": 0, "show": False, "rate": 0, "showPower": False},
        }
        energy = EnergyFlow.from_dict(raw)
        assert energy.pv_panel.power == 1000
        assert energy.pv_panel.show is True
        assert energy.battery.show is False


class TestAlertInfo:
    def test_ok(self) -> None:
        alert = AlertInfo.from_dict({"code": "0000", "title": "OK", "desc": "ok"})
        assert alert.is_ok is True

    def test_not_ok(self) -> None:
        alert = AlertInfo.from_dict({"code": "0040", "title": "AC voltage RMS over", "desc": "unstable"})
        assert alert.is_ok is False


class TestChartData:
    def test_from_dict(self) -> None:
        raw = {
            "legend": ["Power Generation"],
            "xAxisData": ["01", "02", "03"],
            "series": [{"stack": "", "name": "2026", "data": [10, 20, None]}],
        }
        chart = ChartData.from_dict(raw)
        assert chart.legend == ["Power Generation"]
        assert len(chart.x_axis_data) == 3
        assert chart.series[0].data == [10, 20, None]


class TestWeather:
    def test_from_dict(self) -> None:
        raw = {
            "days": 7,
            "temperatureUnit": "Celsius",
            "list": [
                {
                    "datetime": "2026-01-01",
                    "temp": 20,
                    "tempMax": 25,
                    "tempMin": 15,
                    "icon": "sunny",
                    "week": "Monday",
                    "conditions": "Clear",
                },
            ],
        }
        weather = Weather.from_dict(raw)
        assert weather.days == 7
        assert len(weather.forecasts) == 1
        assert weather.forecasts[0].temp == 20


class TestSiteStatusCounts:
    def test_counts(self) -> None:
        raw = {"siteCount": 3, "statusMap": {"0": 2, "-1": 1}}
        counts = SiteStatusCounts.from_dict(raw)
        assert counts.online_count == 2
        assert counts.offline_count == 1


class TestPlaybackData:
    def test_from_dict(self) -> None:
        raw = {
            "overview": {
                "legend": ["playback"],
                "xAxisData": ["00:00", "00:05"],
                "series": [{"name": "playback", "data": [0, 10]}],
            },
            "modules": [
                {"plcSN": "AAA_1", "addr": 1, "data": [0, 5]},
            ],
            "unit": "W",
        }
        pb = PlaybackData.from_dict(raw)
        assert len(pb.modules) == 1
        assert pb.modules[0].plc_sn == "AAA_1"
        assert pb.overview.series[0].data == [0, 10]


class TestDateStatistics:
    def test_from_dict(self) -> None:
        raw = {
            "power": "5.5",
            "consumption": "0",
            "economic": "2.5",
            "powerUnit": "kWh",
            "consumptionUnit": "kWh",
            "economicUnit": "USD",
        }
        ds = DateStatistics.from_dict(raw)
        assert ds.power == "5.5"
        assert ds.economic_unit == "USD"