import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// 로컬 파일 접근을 허용하기 위한 Chrome 옵션
Config.setChromiumOpenGlRenderer("angle");
Config.setDelayRenderTimeoutInMilliseconds(30000);
Config.setChromiumDisableWebSecurity(true);
