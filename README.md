# Shibboleth Addon Module for Odoo

## Overview
This module is a fork of [https://github.com/OCA/server-auth](https://github.com/OCA/server-auth) that uses a proxy server providing
authentication headers for an SSO such as Shibboleth.  Unfortunately, that addon has not been updated since
[Odoo 13.0](https://github.com/OCA/server-auth/blob/13.0/auth_from_http_remote_user) and some of the underlying object models have changed.  This project updates the user model extension and authentication checks to work with Odoo 17.0.

## Why I did this
Odoo can support saml2 directly, but I am already using Apache's shibboleth
module in a number of other places, and I have already worked out the
certificate handling and shibboleth peering.  Letting Apache handle the
SSO is less work for me than getting pysaml configured (not to mention that
this is cheaper).

## Apache Configuration
My configuration uses Apache2 acting as a proxy to Odoo.  The Proxy configuration in my case is:

```apacheconf
#######################################################
#
# ODOO proxy
#
# Some info on this proxy setup for ODOO here:
#       https://apps.odoo.com/apps/modules/9.0/auth_from_http_remote_user/
#
#######################################################

ProxyRequests Off
ProxyPreserveHost On
ProxyAddHeaders On

#
# Odoo runs in a docker container that doesn't need
# to have any ports exposed - we proxy directly to
# the container's network interface
#
ProxyPass / "http://172.28.0.2:8069/"
ProxyPassReverse / "http://172.28.0.2:8069/"

ProxyPass /longpolling/ http://172.28.0.2:8072/ retry=0
ProxyPassReverse /longpolling/ http://172.28.0.2:8072/ retry=0

#
# to avoid messing with SSL in Odoo, let Odoo run plain
# old HTTP.  Pass this header through the proxy to let
# Odoo know we are doing this, so that it can correctly
# generate links
#
RequestHeader set X-Forwarded-Proto "https" env=HTTPS

#
# This proxy server requires the user to be authenticated
# with shibboleth
#
<Location />
        AuthType "shibboleth"
        ShibRequireSession on
        ShibUseEnvironment On
        require shibboleth
</Location>

SSLOptions +StdEnvVars

#
# Scrub our authentication headers in the event that a user injects
# their own.  This makes it so that if someone connects directly to
# the Odoo, bypassing the proxy, the header won't be passed through.
# This is especially important because the subsequent RequestHeader
# has a condition that Shibboleth environment variables are set.
# Scrubbing this header from the incoming proxy request ensures
# these headers will be empty, not hijacked by the end user.
# Note this is done "early"
#
RequestHeader unset Remote-User early
RequestHeader unset Shib-Session early

#
# If shibboleth set variables indicating an active session, pass these
# through the proxy as request headers.  As mentioned above, this will
# not have any effect if there is no shibboleth session, which is why
# we scrubbed these headers early.
#
RequestHeader set Remote-User %{SHIB_mail}e env=SHIB_mail
RequestHeader set Shib-Session %{SHIB_Shib_Session_ID}e env=SHIB_Shib_Session_ID
```