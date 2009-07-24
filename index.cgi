#!/usr/bin/perl -w
###############################################################################
# Changelog-Generation from Bugzilla Script
# Written by Michael Botsko, for use with Bugzilla.
# Free for any use, editing, redistribution, etc.
# www.botsko.net / botsko@gmail.com
###############################################################################

# $Id: index.cgi,v 1.1 2007-10-16 17:16:03 botskonet Exp $

###############################################################################
# YOU MAY EDIT THESE VARIABLES

  use lib ".";
  require "config.cgi";
  
###############################################################################
# USUALLY NO NEED TO EDIT ANYTHING BELOW THIS LINE

  my $verCurrent;

# @@@@@@ DATABASE CONNECT @@@@@@

  use DBI;
  my $dbh = DBI->connect("DBI:mysql:$db:$host:$port", $user, $pass);

# @@@@@@ GET/POST QUERY STRING SUBROUTINES @@@@@@

  sub populateQueryFields {
    %queryString = ();
    my $tmpStr = $ENV{ "QUERY_STRING" };
    @parts = split( /\&/, $tmpStr );
    foreach $part (@parts) {
      ( $name, $value ) = split( /\=/, $part );
      $queryString{ "$name" } = $value;
    }
  }

  sub populatePostFields {
    %postFields = ();
    read( STDIN, $tmpStr, $ENV{ "CONTENT_LENGTH" } );
    @parts = split( /\&/, $tmpStr );
    foreach $part (@parts) {
      ( $name, $value ) = split( /\=/, $part );
      $value =~ ( s/%23/\#/g );
      $value =~ ( s/%2F/\//g );
      $postFields{ "$name" } = $value;
    }
  }

# @@@@@@ DISPLAY HTML & RESULTS @@@@@@

print "Content-type: text/html\n\n";

print "
<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\"
    \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">
<html xmlns=\"http://www.w3.org/1999/xhtml\">
<head>
<meta http-equiv=\"Content-Type\"
content=\"text/html; charset=windows-1252\" />
<meta name=\"author\" content=\"J.Reiser\" />
<title>Bugzilla Changelog</title>
<link rel=\"stylesheet\" type=\"text/css\" href=\"layout.css\" />
<link rel=\"stylesheet\" type=\"text/css\" href=\"color2.css\" />
</head>
<body>

<h1>Bugzilla Changelog Generator</h1>

 <body>

  <div id=\"main-menu\">
    <h3>Product Menu</h3>
      <ul id=\"left\">";

  # @@@@@@ GENERATE PRODUCT MENU @@@@@@

    my $menu_sql_query = "SELECT id, name FROM products ORDER BY name";

    my $menu_sth = $dbh->prepare($menu_sql_query);
    $menu_sth->execute;

  while(@row = $menu_sth->fetchrow_array) {
    print "
      <li><a href=\"index.cgi?prod_id=$row[0]\">$row[1]</a></li>";
  }

  print"
      </ul>
  </div>

  <div id=\"content\">";

  # @@@@@@ DISCOVER PRODUCT-SPECIFIC VERSIONS WITH RESOLVES @@@@@@

  &populateQueryFields;
  $prod_id = $queryString{"prod_id"};

    my $ver_sql_query = "
      SELECT value FROM milestones
      WHERE product_id = \"$prod_id\"
      ORDER BY sortkey,value DESC";

    my $ver_sth = $dbh->prepare($ver_sql_query);
    $ver_sth->execute;

  while(@row = $ver_sth->fetchrow_array) {
    $verCurrent = $row[0];

    print "
      <p>
      <div id=\"footer\">
        <span class=\"version-title\">$verCurrent</span> <a href=\"make_html.cgi?prod_id=$prod_id&ver_id=$verCurrent\">[HTML]</a>
      </div>
      <p>";

    # @@@@@@ DISCOVER ANY RESOLVED BUGS FOR CURRENT PRODUCT-VERSION @@@@@@

    my $bug_sql_query = "
      SELECT
        bugs.bug_id,
        bugs.short_desc,
        components.name,
        bugs.bug_severity
      FROM
        bugs,
        components
      WHERE bugs.product_id = $prod_id
      AND bugs.bug_status = \"RESOLVED\"
      AND bugs.resolution = \"FIXED\"
      AND bugs.component_id = components.id
      AND bugs.target_milestone = \"$verCurrent\"
      ORDER BY bugs.lastdiffed DESC";

    my $bug_sth = $dbh->prepare($bug_sql_query);
    $bug_sth->execute;

    while(@row = $bug_sth->fetchrow_array) {
      print "
       <a href=\"$bURL/show_bug.cgi?id=$row[0]\">$row[0]</a>:
       &nbsp;<b>[$row[2]]</b> $row[1] <i>($row[3])</i><br />";
    }

  print "
    </p>";

  }

  print "
</body>
</html>";


# @@@@@@ END OF FILE
