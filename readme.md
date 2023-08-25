# Cloudflare WAF Eligibility Checker

Python script loops through each zone on an account to check its WAF Update Eligibility Status.
Prompts for credentials.
Prints to screen or writes to file waf_compatibility_check.txt

To use: $ python waf-checker.py 

As per dev docs: https://developers.cloudflare.com/waf/reference/migration-guides/waf-managed-rules-migration/

Example compatability response:
{
	"result": {
		"compatible": false
	},
	"success": true,
	"errors": [],
	"messages": []
}
