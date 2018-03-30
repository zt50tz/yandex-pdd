# yandex_pdd

Library for yandex domain service.

### Installation

```python
pip install yandex-pdd
```

### Example

```python
from yandex_pdd import YandexPdd
app = YandexPdd('domain.com', '<TOKEN>')
app.email_add('login', 'password')  # add email
app.email_list_all()  # full list of emails
```

Methods
----

All methods from page https://tech.yandex.ru/pdd/doc/. Naming of methods is getting by removing slashes from api path, so:
- api "email/add" become method ```email_add```
- api "email/ml/add" - become method ```email_ml_add```
- and so on

##### Domain
- ```domain_list``` - Domain list page
- ```domain_list_all``` - Domain list all
- ```domain_register``` — Register domain
- ```domain_registration_status``` - domain_registration_status
- ```domain_details``` - Domain details
- ```domain_delete``` - Domain delete
- ```domain_settings_set_country``` - Set country for domain

##### Email
- ```email_add``` - Email add
- ```email_list``` - Email list page
- ```email_list_all``` - Email list all
- ```email_edit``` - Email edit
- ```email_del``` - Email delete
- ```email_counters``` - Email counters - messages

##### Mail list
- ```email_ml_add``` / ```ml_add``` - Mail list add
- ```email_ml_list``` / ```ml_list``` - List of mail lists
- ```email_ml_subscribe``` / ```ml_subscribe``` - Mail list subscribe email
- ```email_ml_unsubscribe``` / ```ml_unsubscribe``` - Email list unsubscribe email
- ```email_ml_get_can_send_on_behalf``` / ```ml_send_get``` - Email list get subscriber can send mail by name of mail list
- ```email_ml_set_can_send_on_behalf``` / ```ml_send_set``` - Email list set subscriber can send mail by name of mail list

##### Import mailbox
- ```import_check_settings``` - Check that yandex can import server
- ```import_start_one_import``` - Import mailbox
- ```import_check_imports``` - Check status of imports
- ```import_stop_all_imports``` - Stop all imports

##### Admin
- ```deputy_add``` - Add subadmin for domain
- ```deputy_list``` - Get subadmin list for domain
- ```deputy_delete``` - Remove subadmin from domain

##### DKIM
- ```dkim_status``` - DKIM get status
- ```dkim_enable``` - DKIM enable
- ```dkim_disable``` - DKIM disable

##### DNS
- ```dns_add``` - DNS add record
- ```dns_list``` - DNS get records
- ```dns_edit``` - DNS edit record
- ```dns_del``` - DNS delete record

##### AUTH ACTIONS
- ```email_get_oauth_token``` - Get oauth token
- ```passport_oauth``` - Get link for auth