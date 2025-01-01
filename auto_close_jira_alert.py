import re

from jira import JIRA
from config.auto_search_dir import data_config
from send_to_telegram_email.send_to_TG_email import send_to_telegram
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CloseAlrt:
    def __init__(self):
        self.JiraLogin = data_config["JiraOptions"]["JiraLogin"]
        self.JiraPassword = data_config["JiraOptions"]["JiraPassword"]
        self.JiraAddress = data_config["JiraOptions"]["JiraAddress"]
        self.jira = JIRA(self.JiraAddress,
                         basic_auth=(self.JiraLogin, self.JiraPassword))
        self.process_alerts()

    def update_field(self, id_alert, field, issue):
        # Проверяем, существует ли поле в метаданных задачи
        if field in self.jira.editmeta(issue)['fields']:
            # Получаем разрешённые значения для данного поля
            field_options = self.jira.editmeta(issue)['fields'][field][
                'allowedValues']

            # Ищем значение, соответствующее id_alert среди разрешённых
            # значений
            field_value = next((option['id'] for option in field_options if
                                option['id'] == id_alert), None)

            # Если найдено подходящее значение, обновляем поле задачи
            if field_value:
                issue.update(fields={field: {'id': field_value}})
        else:
            # Если поле не найдено, выводим сообщение в консоль
            print(f"Поле {field} не найдено для задачи {issue.key}")

    def take_issues(self, jql_str, transition_id, message):
        issues = self.jira.search_issues(jql_str)
        for issue in issues:
            self.jira.transition_issue(issue, transition_id)
            send_to_telegram(
                f'{message} <a href="https://dev.taxcom.ru/jira/browse/\
                {issue.key}">{issue.key}</a>')

    def close_alert(self, closing_query):
        issues_to_close = self.jira.search_issues(closing_query)
        # перебираем каждую найденную задачу
        for issue in issues_to_close:
            # находим комментарии
            user_comments = [
                comment
                for comment in issue.fields.comment.comments
                if re.search(r"fokinkv$", comment.author.key)
            ]
            # если есть комментарии от текущего пользователя, то пишем
            # нужные слова в "проделанных действий
            if user_comments:
                self.update_field('13509', 'customfield_14208', issue)
                closing_message = ('Были проделаны действия, подробности в '
                                   'комм.')
            else:
                self.update_field('16503', 'customfield_14208', issue)
                closing_message = ('Автоматическое закрытие, действия не '
                                   'проделывались')

            issue.update(fields={'customfield_15811': closing_message})
            self.update_field('12102', 'customfield_12407', issue)
            self.jira.transition_issue(issue, '141')
            send_to_telegram(
                f'Закрыл задачу <a href="https://dev.taxcom.ru/jira/browse/\
                {issue.key}">{issue.key}</a>')

        if not issues_to_close:
            print('Закрытых нет')

    def process_alerts(self):
        # взятие в работу
        major_alerts_query = ('project = GSAA AND issuetype = Alert AND '
                              'status = "To Do" AND assignee in ('
                              'currentUser()) AND priority = Major')
        self.take_issues(major_alerts_query, '101', 'Взял в работу задачу')
        # закрытие задач
        closing_query = ('project = GSAA AND issuetype = Alert AND status in '
                         '("In Progress", "To Do") AND assignee in ('
                         'currentUser()) AND priority = Major AND cf[14508] '
                         'is not null AND description !~ "закрыть вручную"')
        self.close_alert(closing_query)


# Использование класса для выполнения запроса и создания таблицы
db_handler = CloseAlrt()
