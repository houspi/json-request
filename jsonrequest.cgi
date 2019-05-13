#!/usr/bin/perl

use strict;
use warnings;

use CGI;
use HTTP::Status qw(:constants :is status_message);
use HOP::Lexer;

my %Substitutions = (
    "%VALUE%" => \&replace_VALUE,
    "%ARRAY%" => \&replace_ARRAY,
    "rand"    => \&replace_rand,
    "one"    => \&replace_one,
);

my %AllowedMethods = (
    "GET"     => 1,
    "POST"    => 0,
    "HEAD"    => 0,
    "PUT"     => 0,
    "DELETE"  => 0,
    "CONNECT" => 0,
    "OPTIONS" => 0,
    "TRACE"   => 0,
);

my $ValidKey = "zbg6fa,sht.uags";
my $BaseDir = "/home/edi/epam/jsonrequest/data/";
my $IndexFile = "index.json";

my $http_code = HTTP_OK;
my $content = "";

my $cgi = CGI->new();

my $method = $cgi->request_method();
my $auth_key = $cgi->param('auth_key');

my $path = $cgi->param('path') || '';
$path =~ s/\.\.//g;
$path =~ s/^\/+|\/+$//g;

if ( $auth_key ne $ValidKey) {
    $http_code = HTTP_FORBIDDEN;
} elsif ( ! $AllowedMethods{$method} ) {
    $http_code = HTTP_METHOD_NOT_ALLOWED;
} elsif ( !-f $BaseDir.$path."/".$IndexFile) {
    $http_code = HTTP_NOT_FOUND;
} else {
    if ( open(INDEX, $BaseDir.$path."/".$IndexFile) ) {
        undef $/;
        $content = <INDEX>;
        close INDEX;
    } else {
        $http_code = HTTP_NOT_FOUND;
    }
}

if ( $http_code eq HTTP_OK) {
    while ( $content =~ /(%(\w+?)\((.+?)\)%)/g ) {
        my $macros = $1;
        my $key_word = $2;
        my $params = $3;
        if ( exists($Substitutions{$key_word}) ) {
            $content =~ s/\Q$macros/$Substitutions{$key_word}->($params)/e;
        }
    }
}

#            -type   => 'application/json',
#            -type   => 'text/plain',
print   $cgi->header(
            -type   => 'application/json',
            -status => $http_code . " " . status_message( $http_code ),
            -Content_length => length($content),
        );
print $content;

sub replace_VALUE {
    my $value = "String";
    return "\"$value\"";
}

sub replace_ARRAY {
    my @list=();
    foreach (qw(a b c))  {
        push(@list, "\"$_\"");
    }
    my $value = join(",", @list);
    return "[$value]";
}

sub replace_rand {
    my $param = shift;
    my $value=0;
    if ($param =~ /(\d+),\s*(\d+)/) {
        if ($2 >= $1) {
            $value = int(rand($2-$1+1)) + $1;
        } else {
            $value=0;
        }

    } else {
        $value=0;
    }
    return $value;
}

sub replace_one {
    my $param = shift;
    my @list = ();
    my $size;
    while ( $param =~ /'(.*?)',?\s*/g ) {
        $size = push(@list, "\"$1\"");
    }
    if ($size) {
        return $list[int(rand($size))];
    } else {
        return "";
    }
}
