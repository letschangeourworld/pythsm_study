/**
 * Vitna 통역방송 시스템 - 자동 환경 감지
 * - IP 접속: 테스트 모드 (HTTP + 포트)
 * - 도메인 접속: 운영 모드 (HTTPS + 표준 포트)
 */
const AppConfig = (() => {
  const host     = window.location.hostname;
  const protocol = window.location.protocol;
  const isIP     = /^\d+\.\d+\.\d+\.\d+$/.test(host) || host === 'localhost';
  const isHTTPS  = protocol === 'https:';

  // 운영 모드: 도메인 접속 (HTTPS)
  const isProd   = !isIP && isHTTPS;

  const apiBase    = isProd
    ? `https://${host}`                    // translate.vitna.net
    : `http://${host}:19000`;              // 10.x.x.x:19000

  const liveKitUrl = isProd
    ? `wss://${host}:7880`                 // wss://translate.vitna.net:7880
    : `ws://${host}:17880`;               // ws://10.x.x.x:17880

  const wsUrl = isProd
    ? `wss://${host}/ws`                   // wss://translate.vitna.net/ws
    : `ws://${host}:19000/ws`;            // ws://10.x.x.x:19000/ws

  const urls = isProd ? {
    portal:      `https://${host}`,
    admin:       `https://${host}/login.html`,
    listener:    `https://${host}/listen.html`,
    interpreter: `https://${host}/interpreter-test.html`,
    grafana:     `https://${host}:19300`,
    minio:       `https://${host}:19011`,
    apiDocs:     `https://${host}/api/docs`,
  } : {
    portal:      `http://${host}:19000`,
    admin:       `http://${host}:19000/login.html`,
    listener:    `http://${host}:19081/listen.html`,
    interpreter: `http://${host}:19000/interpreter-test.html`,
    grafana:     `http://${host}:19300`,
    minio:       `http://${host}:19011`,
    apiDocs:     `http://${host}:19000/api/docs`,
  };

  console.log(`[AppConfig] 모드: ${isProd ? '🌐 운영(HTTPS)' : '🔧 테스트(HTTP)'}`);
  console.log(`[AppConfig] API: ${apiBase}`);
  console.log(`[AppConfig] WS:  ${wsUrl}`);
  console.log(`[AppConfig] LK:  ${liveKitUrl}`);

  return {
    host, apiBase, wsUrl, liveKitUrl, urls,
    isProd, isTest: !isProd,
    // LiveKit room 매핑
    roomMap: {
      english:  'room_en',
      japanese: 'room_ja',
      chinese:  'room_zh',
    }
  };
})();

window.AppConfig = AppConfig;
