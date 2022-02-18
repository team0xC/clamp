// CSE545 - Team 12 (team0xC) 
// PHP Patcher codes
// References: 
// [1] "How can I sanetize user input with PHP?", https://stackoverflow.com/questions/129677/how-can-i-sanitize-user-input-with-php (accessed February 17 2022)

<?php

class php_patch {

private $input:
private $output;
private $command;
private $sql_str;

// Preventing output from being placed in an untrusted location - Put NULL.
	public function designated_ouput($input){
		$output = '';
		return $output;
	}

// Replaces ", ', <, >, & characters in the input string
	public function removing_specialchars($input){
		$output = htmlspecialchars($input, ENT_QUOTES); 
		return $output;
	}
// Prevents to add another command in the initial command
	public function sanitizing_commands($command){
		$command1 = escapeshellcmd ( $command ); 
		return $command1;
	}

// Check for alpha-numerics
	public function sanitizing_commands($input){
		if( !ctype_alnum ( $input )) { 
			echo "Not a valid input";
			$output = htmlspecialchars($input, ENT_QUOTES);
			return $output;
		}
	}

// Populate $mysqli = new mysqli("host", "user", "password", "dbname");
// Then clear special chars  from sqli string
	public function sanitizing_attributes_sql($sql_str){
		$sql_str = $mysqli->real_escape_string($sql_str); 
		return $sql_str;
	}

}
// Sanitize form data
function clean($data)
{
    $data = htmlspecialchars($data);
    $data = stripslashes($data);
    $data = trim($data);
    return $data;
}

// Sanitize user input
function sanitize($stringToSanitize) {
    return addslashes(htmlspecialchars($stringToSanitize));
}
// You can just use the codes themselves instead of creating a function as:
// echo addslashes(htmlspecialchars($stringToSanitize));


// php clean user input
<?php
    function cleanUserInput($userinput) {

  		// Open your database connection

      	$dbConnection = databaseConnect();

  		// check if input is empty

        if (empty($userinput)) {
          return;
        } else {
        
// Strip any html characters

        $userinput = htmlspecialchars($userinput);
		// Clean input using the database 
        $userinput = mysqli_real_escape_string($dbConnection, $userinput);
        }

  	  // Return a cleaned string

      return $userinput;
    }
?>
?>
