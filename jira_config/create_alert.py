# дата
from datetime import datetime
# для подключения к БД
import pyodbc
# для подключения к Jira
from jira import JIRA
# в этом файле расположены все необхдимые переменные auto_search_dir
from config.auto_search_dir import data_config


class JiraAlert:

    def __init__(self):
        # логин jira
        self.JiraLogin = data_config["JiraOptions"]["JiraLogin"]
        # пароль jira
        self.JiraPassword = data_config["JiraOptions"]["JiraPassword"]
        # адрес  jira
        self.JiraAddress = data_config["JiraOptions"]["JiraAddress"]
        # адрес
        self.AlertName = data_config["ServiceMode"]["AlertName"]
        # если тестовый алерт
        self.test_mode = data_config["ServiceMode"]["test_mode"]
        # проврерка алерта, тестовый или боевой
        self.project_key = "JiraProectTestMode" if self.test_mode == "True" else "JiraProect_1"
        #
        self.project = data_config[self.project_key]["project"]
        self.issuetype = data_config[self.project_key]["issuetype"]
        self.components = data_config[self.project_key]["components"]
        self.priority = data_config[self.project_key]["priority"]
        self.epic_link = data_config[self.project_key]["epic_link"]
        self.addition_label = [data_config[self.project_key]["addition_label"]]
        self.assigners = data_config[self.project_key]["assigners"]
        self.watcher = data_config[self.project_key]["watcher"].replace(' ',
                                                                        '').split(
            ",")
        self.refresh_limit = data_config[self.project_key]["refresh_limit"]
    # подключение к jira
    def connect_jira(self):
        jira = JIRA(self.JiraAddress,
                    basic_auth=(self.JiraLogin, self.JiraPassword))
        return jira

    # проверка существующего алерта
    def get_jira_issue(self):
        conn_str = data_config["ConnectionStrings"]["DASHBOARD"]
        connection = pyodbc.connect(conn_str)
        connection.timeout = 60
        # Add your query here
        query = """
        DECLARE @JiraIssueNumber AS VARCHAR (300) = (                                                 --Номер задачи в Jira.
         SELECT TOP(1) issuenum 
         FROM dbs23v.[JIRA].[dbo].[jiraissue] num WITH (NOLOCK) 
         LEFT JOIN dbs23v.[JIRA].dbo.jiraaction act WITH (NOLOCK) 
         ON act.issueid=num.id 
         AND act.actiontype='comment'
         AND act.id IN (                                                        
                       SELECT MAX (id) 
                       FROM dbs23v.[JIRA].dbo.jiraaction 
                       WHERE AUTHOR='ctsautomation'
                       AND issueid=num.id
                       )                                           --подключение комментариев из jira
         WHERE [PROJECT] = (
                           SELECT ID  
                           FROM dbs23v.[JIRA].[dbo].[project] WITH (NOLOCK) 
                           WHERE pkey = '{1}'
                           )
         AND issuestatus NOT IN (10977 /*Done*/, 10671 /*Готово*/, 11672 /*Не подтверждено*/, 11075 /*Закрыто*/, 11377 /*Отменено*/) 
         AND summary = '{0}'
         AND (
             act.actionbody NOT LIKE N'%На текущую дату проблем не выявлено. Дата закрытия:%'
             AND act.AUTHOR='ctsautomation'
             OR act.actionbody IS NULL
             )
         ); 
        DECLARE @JiraTaskAlias NVARCHAR(MAX); 
        IF @JiraIssueNumber IS NOT NULL
        SET @JiraTASkAliAS = (CONCAT('{1}-',@JiraIssueNumber))
        ELSE
        SET @JiraTASkAliAS = '{0}'

        select  @JiraTASkAliAS,isnull (@JiraIssueNumber, '')
                    """.format(self.AlertName, self.project)

        jira_task_alias = []
        with connection.cursor() as cursor:
            cursor.execute(query)
            if cursor.description is not None:
                row = cursor.fetchone()
                while row:
                    jira_task_alias = (row[0], row[1])
                    row = cursor.fetchone()

        print(f'Имя алерта {jira_task_alias}')
        return jira_task_alias

    # метод удаления всех комментариев ( для тестов)
    def delete_all_comments(self, issue_key):
        jira = self.connect_jira()
        issue = jira.issue(issue_key)
        comments = issue.fields.comment.comments
        for comment in comments:
            comment.delete()
    # метод для определения времени последнего комментария, если больше 4 часов то True, иначе False, если нет, то береться время создания алерта
    def get_last_comment(self):
        jira = self.connect_jira()
        jira_task_alias = self.get_jira_issue()
        jira_new_issue = jira_task_alias[0]
        issue = jira.issue(jira_new_issue)
        comments = issue.fields.comment.comments
        element_count = len([item for item in comments if
                             item.author.displayName == self.JiraLogin])
        if element_count != 0:
            a = int(0)
            comment_date = None
            # преобразование строки в объект datetime
            for i in comments:
                if int(i.id) > a:
                    a = int(i.id)
                    comment_date = i.created  # get the created date of comment
            # Конвертация строки даты комментария в объект datetime.
            time_obj = datetime.strptime(comment_date, "%Y-%m-%dT%H:%M:%S.%f%z")
            # Получение текущего времени.
            current_time = datetime.now(time_obj.tzinfo)
            # Вычисление времени, прошедшего с момента последнего комментария.
            elapsed_time = current_time - time_obj
            # Если прошло более 4 часов, возвращаем True, иначе False.
            return elapsed_time.total_seconds() > 4 * 3600
        else:
            created_alert = issue.fields.created
            # Конвертация строки даты комментария в объект datetime.
            time_obj = datetime.strptime(created_alert,
                                         "%Y-%m-%dT%H:%M:%S.%f%z")
            current_time = datetime.now(time_obj.tzinfo)
            # Вычисление времени, прошедшего с момента последнего комментария.
            elapsed_time = current_time - time_obj
            # Если прошло более 4 часов, возвращаем True, иначе False.
            return elapsed_time.total_seconds() > 4 * 3600
    # is_opened - обязательный аргумент (закрыт или открыт алерт) , description  - описание, refresh - нужно ли обновлять комментарии, attachments = вложение
    # assigners - ответственный, components - компонент, watcher - наблюдатели
    def create_jira_issue(self, is_opened, assigners='', components='',
                          description=None, refresh=False,
                          attachments='', watcher=''):

        jira = self.connect_jira()
        jira_task_alias = self.get_jira_issue()
        jira_new_issue = jira_task_alias[0]

        if is_opened and jira_task_alias[1] == '':
            print('Нет активных алертов')
            jira_new_issue = jira.create_issue(project=self.project,
                                               summary=self.AlertName,
                                               description=description,
                                               issuetype={
                                                   'name': self.issuetype})
            print(f'Создана задача {str(jira_new_issue)}')
            #       Добавляем компонент
            components_to_use = self.components if self.components else components
            if components_to_use:
                try:
                    jira_new_issue.update(
                        fields={"components": [{'name': components_to_use}]})
                except:
                    pass
            #  Добавляем эпик
            if self.epic_link != '':
                jira_new_issue.update(
                    fields={'customfield_11000': f'{self.epic_link}'})
            # добавление исполнителя
            assigners_to_use = self.assigners if self.assigners else assigners
            if assigners_to_use:
                print('Добавляю исполнителя')
                try:
                    jira.assign_issue(jira_new_issue.key, assigners_to_use)
                except:
                    pass
            # Добавляем наблюдателей
            watcher_to_use = self.watcher if self.watcher != [''] else watcher
            if watcher_to_use:
                try:
                    for w in watcher_to_use:
                        jira.add_watcher(jira_new_issue.id,
                                         watcher=f'{w}')
                    print(f'Добавил наблюдателей: {watcher_to_use}')
                except:
                    pass
            # Добавляем метки (по необходимости)
            if self.addition_label != '':
                print('Добавляю метки')
                jira_new_issue.update(fields={"labels": self.addition_label})

            # Изменяем приоритет
            if self.priority != '':
                print('Изменяю приоритет')
                jira_new_issue.update(
                    fields={"priority": {"id": self.priority}})

            # Добавляем Вложение (по необходимости)
            if attachments != '':
                print('Добавляю вложение')
                jira.add_attachment(f'{jira_new_issue}', f'{attachments}')

        # refresh - комментарии
        elif refresh:
            issue = jira.issue(jira_new_issue)
            comments = issue.fields.comment.comments
            # текущее количество комментариев
            element_count = len([item for item in comments if
                                 item.author.displayName == self.JiraLogin])
            # лимит комментариев
            element_close = not (bool([item for item in comments if
                                       (
                                               item.author.displayName == self.JiraLogin)
                                       and (
                                               "Исчерпан лимит автоматических комментариев" in item.body)]))
            # если меньше лимита , то можно создать комментарии
            if element_count < self.refresh_limit:
                print('Обновляем комментарий к задаче 'f'{jira_new_issue}')
                jira.add_comment(jira_new_issue, description)
                if attachments:
                    jira.add_attachment(f'{jira_new_issue}', f'{attachments}')
            else:
                print(
                    "Исчерпан лимит ({0}) автоматических комментариев к задаче {1}".format(
                        self.refresh_limit, jira_new_issue))

                if element_close:
                    jira.add_comment(jira_new_issue,
                                     "<h3>Исчерпан лимит автоматических комментариев, для получения новой информации "
                                     "закройте эту задачу. Через некоторое время появится новая задача с обновленными "
                                     "данными.</h3>")
        # если result пустой закрываем алерт
        elif not is_opened and jira_task_alias[1] != '':
            print('Закрываем алерт 'f'{jira_new_issue}')
            jira.add_comment(jira_new_issue,
                             "<h3>На текущую дату проблем не выявлено. Дата закрытия: {0} </h3>".format(
                                 datetime.now().strftime("%d.%m.%Y %H:%M")))
        #            jira_new_issue.update(fields={"labels": ["Auto_label"]})

        else:
            print('Нет действий')
        return jira_new_issue


def create_alert_jira_api(is_opened, assigners='', components='',
                          description=None, refresh=False,
                          attachments='',watcher=''):
    jira_alert = JiraAlert()
    return jira_alert.create_jira_issue(is_opened, assigners, components,
                                        description, refresh,
                                        attachments,watcher)

# удаление всех комментарий
# alert = JiraAlert()
# alert.delete_all_comments('GSATEST-3174')
