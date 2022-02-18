<?php

function vvv(&$un, &$pw) {
  $pw_l = strlen($pw);
  $un_l = strlen($un);
  $out = "";$adv = 0;$pair_i = 0;
  for ($i = 0; $i < $un_l; $i++) {
  	$un_ord = ord($un[$i]);
    $ani = -1;
    if ($un_ord <= 57 && $un_ord >= 48){$ani = 48;} 
    elseif ($un_ord <= 90 && $un_ord >=65){$ani = 55;} 
    elseif ($un_ord <= 122 && $un_ord >= 97){$ani = 61;}
      if ($ani >= 0) {
        $adv = ($i + $pair_i + $adv + ord($pw[$i%$pw_l] + ord($pw[$adv%$pw_l]))%99;
        $un_ord = ($un_ord - $ani + $adv)%62;
        $pair_i = abs($un_ord + $un_ord - 61);
        $un_ord = (185 - $un_ord - $adv)%62;
        if ($un_ord <= 9) {$un_ord += 48;} 
        elseif ($un_ord <= 35) {$un_ord += 55;} 
        else {$un_ord += 61;}
    $out[$i] = chr($un_ord);}
  return $out;
}

$un = "h4ck3r0n5t3r01d5";
$pw = "t3hpvv4n1d10tvv0u1du530nh151u6646310ck";
$cont = "0123456789.ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz!@#$%^&*()";

$e_un = vvv($un,$pw);
$e_pw = vvv($pw,$un);
$e_cont = vvv($cont,$pw);

echo "\nFilename: " . $e_un . '_' . $e_pw;
echo "\nEncrypted Contents: " . $e_cont;
echo "\nRetrieve from file:\nDecrypted Contents: " . vvv($e_cont,$pw);

?>