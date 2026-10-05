# Third-party assets and security references

All runtime frontend assets are served from the application's own `static/vendor/` directory. Browsing the app does not contact a CDN or font provider.

| Asset | Version | Upstream | License |
| --- | --- | --- | --- |
| Bootstrap CSS | 5.3.8 | [twbs/bootstrap](https://github.com/twbs/bootstrap) | [MIT](../app/static/vendor/licenses/bootstrap.txt) |
| Bootstrap Icons and fonts | 1.13.1 | [twbs/icons](https://github.com/twbs/icons) | [MIT](../app/static/vendor/licenses/bootstrap-icons.txt) |
| Chart.js UMD | 4.5.1 | [chartjs/Chart.js](https://github.com/chartjs/Chart.js) | [MIT](../app/static/vendor/licenses/chartjs.txt) |

The checked-in assets are ready to use. Maintainers can re-fetch these exact versions with `python tools/fetch_vendor.py`; this maintenance command requires internet access. There is no frontend build step.

Security guidance references:

- [CISA: Use Strong Passwords](https://www.cisa.gov/secure-our-world/use-strong-passwords)
- [NIST SP 800-63B-4: Digital Identity Guidelines](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [Flask security considerations](https://flask.palletsprojects.com/en/stable/web-security/)
- [Flask-WTF CSRF protection](https://flask-wtf.readthedocs.io/en/latest/csrf/)

The application's scoring algorithm is educational and is not a NIST compliance assessment or a breach database lookup.
