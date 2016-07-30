<?php

namespace App\AnimeSentinel;

class Downloaders
{
  /**
   * Returns a webpage after executing JavaScript
   *
   * @return string
   */
  public static function downloadJavaScript($url) {
    return ""; //TODO
  }

  /**
   * Downloads webpages behind a cloudflare filter.
   *
   * @return string
   */
  public static function downloadCloudFlare($url, $cookieid = 'cloudflare') {
    if (file_exists(__DIR__.'/../../storage/app/cookies/'.$cookieid)) {
      $cf_data = json_decode(file_get_contents(__DIR__.'/../../storage/app/cookies/'.$cookieid));
    } else {
      Self::requestCloudFlareData($url, $cookieid);
      return Self::downloadCloudFlare($url, $cookieid);
    }

    if ($cookieid === 'kissanime') {
      $cf_data->cookies .= '; password=xF0d5g%2bDfyUirFXabZYgRi17jf9gLeTF; username=kV9SRW%2fZraoO0hm2pEp2AA%3d%3d';
    }

    $curl = curl_init();
    curl_setopt($curl, CURLOPT_URL, $url);
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($curl, CURLOPT_FOLLOWLOCATION, 1);
    curl_setopt($curl, CURLOPT_HTTPHEADER, [
      'Cookie: '.$cf_data->cookies,
      'User-Agent: '.$cf_data->agent,
    ]);
    $response = curl_exec($curl);
    curl_close($curl);

    if (strpos($response, '<title>Please wait 5 seconds...</title>') !== false) {
      Self::requestCloudFlareData($url, $cookieid);
      return Self::downloadCloudFlare($url, $cookieid);
    }

    return $response;
  }

  private static function requestCloudFlareData($url, $cookieid = 'cloudflare') {
    exec('python '. __DIR__ .'/CloudFlare.py "'. $url .'" "'. $cookieid .'"');
  }
}