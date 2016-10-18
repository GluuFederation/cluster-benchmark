from mechanicalsoup import Browser
from mechanicalsoup import Form

# disable ssl warnings (for now)
try:
    import urllib3
except ImportError:
    from requests.packages import urllib3
finally:
    urllib3.disable_warnings()


def get_browser():
    """Gets an instance of :class:`mechanicalsoup.Browser`.
    """
    browser = Browser(soup_config={"features": "html.parser"})
    return browser


def oxtrust_login(browser, base_url, username, password,
                  verify_ssl=True, timeout=None):
    """Makes login request.

    :param browser: An instance of :class:`mechanicalsoup.Browser`.
    :param base_url: Base URL of oxTrust.
    :param username: Username of an account.
    :param password: Password of an account.
    :param verify_ssl: Verify SSL cerficate in target server.
    :returns: An instance of monkeypatched :class:`requests.Response`.
    """
    # get the oxTrust homepage
    oxtrust_page = browser.get("{}".format(base_url), verify=verify_ssl,
                               timeout=timeout)

    # oxTrust homepage uses meta for page redirection
    refresh_url = oxtrust_page.soup.select("meta")[0]["content"].split("=")[-1]

    # redirect user to login page
    login_page = browser.get("{}/{}".format(base_url, refresh_url),
                             timeout=timeout)

    # if we get dropdown with username text on it, then we already logged in
    user_header = login_page.soup.select_one(".user-header p")
    if user_header and user_header.text.strip() == username:
        return login_page

    # try to make login attempt
    login_form = login_page.soup.select("#loginForm")[0]
    login_form.select("#loginForm:username")[0]["value"] = username
    login_form.select("#loginForm:password")[0]["value"] = password

    auth_page = browser.submit(login_form, login_page.url)
    querystring = auth_page.url.split("#")[-1]
    login_page = browser.get(
        "{}/authentication/getauthcode?{}".format(base_url, querystring),
        timeout=timeout,
    )
    return login_page


def oxtrust_logout(browser, base_url, verify_ssl=True, timeout=None):
    """Makes logout request.

    :param browser: An instance of :class:`mechanicalsoup.Browser`.
    :param base_url: Base URL of oxTrust.
    :param verify_ssl: Verify SSL cerficate in target server.
    :returns: An instance of monkeypatched :class:`requests.Response`.
    """
    browser.get("{}/logout".format(base_url), verify=verify_ssl,
                timeout=timeout)
    page = browser.get("{}/authentication/finishlogout".format(base_url),
                       timeout=timeout)
    return page


def rp_login(browser, base_url, username, password,
             verify_ssl=True, timeout=None):
    """Makes login request.

    :param browser: An instance of :class:`mechanicalsoup.Browser`.
    :param base_url: Base URL of RP site.
    :param username: Username of an account.
    :param password: Password of an account.
    :param verify_ssl: Verify SSL cerficate in target server.
    :returns: An instance of monkeypatched :class:`requests.Response`.
    """
    # get the RP
    login_page = browser.get("{}/authorize/".format(base_url),
                             verify=verify_ssl, timeout=timeout)

    # if we get inum, we're already logged in
    if "inum" in login_page.text:
        return login_page

    # something's wrong in RP site
    if login_page.status_code == 500:
        return login_page

    # try to make login attempt
    login_form = login_page.soup.select_one("#loginForm")
    login_form.select_one("#loginForm:username")["value"] = username
    login_form.select_one("#loginForm:password")["value"] = password

    auth_page = browser.submit(login_form, login_page.url)

    # redirected to Allow/Don't Allow page
    allow_form = Form(auth_page.soup.select_one("#authorizeForm"))
    submit = auth_page.soup.select_one("#authorizeForm:allowButton")

    allow_form.choose_submit(submit)
    page = browser.submit(allow_form, auth_page.url)
    return page


def rp_logout(browser, base_url, verify_ssl=True, timeout=None):
    """Makes logout request.

    :param browser: An instance of :class:`mechanicalsoup.Browser`.
    :param base_url: Base URL of RP site.
    :param verify_ssl: Verify SSL cerficate in target server.
    :returns: An instance of monkeypatched :class:`requests.Response`.
    """
    browser.get("{}/logout".format(base_url), verify=verify_ssl,
                timeout=timeout)
    page = browser.get(base_url, timeout=timeout)
    return page
