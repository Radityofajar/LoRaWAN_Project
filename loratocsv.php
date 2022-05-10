<?php
class LoRa{
public $link='';
function __construct($node01, $temperature, $node02, $humidity, $node03, $dust)
{
	$this->connect();
	$this->storeInDB($node01, $temperature, $node02, $humidity, $node03, $dust);
}
 
function connect()
{
	$this->link = mysqli_connect('localhost','root','') or die('Cannot connect to the DB');
	mysqli_select_db($this->link,'WiComAI_SR_LoRa_T') or die('Cannot select the DB');
}
 
function storeInDB($node01, $temperature, $node02, $humidity, $node03, $dust)
{
	$query = "insert into LoRa set node01='".$node01."', temperature='".$temperature."', node02='".$node02."', humidity='".$humidity."', node03='".$node03."', dust='".$dust."'";
	$result = mysqli_query($this->link,$query) or die('Errant query:  '.$query);
}
 
}

$conn = mysqli_connect("localhost","root","") or die("cann't connect");
mysqli_select_db($conn, 'WiComAI_SR_LoRa_T');
$csvfile=fopen("loraData.csv","a")or die("Unable to open file!");
/* $sql = mysqli_query($conn, "SELECT * FROM lora") or die("cann't connect");

$row = mysqli_fetch_assoc($sql);
$seperator = "";
$comma = "";
foreach($row as $name => $value)
	{
		$seperator .= $comma .'' .str_replace('','""',$name);
		$comma = ",";
	}
$seperator .= "\n";
fwrite($csvfile, $seperator); */

if($_GET['node01'] != '' and  $_GET['temperature'] != '')
{
	$LoRa=new LoRa($_GET['node01'],$_GET['temperature'],$_GET['node02'],$_GET['humidity'],$_GET['node03'],$_GET['dust']);
}
if($_GET['node02'] != '' and $_GET['humidity'] != '')
{
	$LoRa=new LoRa($_GET['node01'],$_GET['temperature'],$_GET['node02'],$_GET['humidity'],$_GET['node03'],$_GET['dust']);
}
if($_GET['node03'] != '' and $_GET['dust'] != '')
{
	$LoRa=new LoRa($_GET['node01'],$_GET['temperature'],$_GET['node02'],$_GET['humidity'],$_GET['node03'],$_GET['dust']);
}

$lastrow = mysqli_fetch_assoc(mysqli_query($conn, "SELECT * FROM lora ORDER BY id DESC LIMIT 1"));
$seperator = "";
$comma = "";
foreach($lastrow as $name => $value)
	{
		$seperator .= $comma .'' .str_replace('','""',$value);
		$comma = ",";
	}
$seperator .= "\n";
fwrite($csvfile, $seperator);
fclose($csvfile);

?>