from mcdreforged.api.all import *
import paramiko

class SSHClient:
    def __init__(self):
        self.client = None

    # 连接到远程服务器
    def connect(self, hostname, username, password, src: CommandSource):
        if self.client is not None and self.client.get_transport() is not None:
            src.reply("已经连接到了SSH服务器")
        else: 
            try:
                src.reply(f"正在连接到 {hostname}...")
                self.client = paramiko.SSHClient()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.client.connect(hostname, username=username, password=password)
                src.reply("成功连接到SSH服务器")
            except Exception as e:
                src.reply(f"连接失败: {e}")

    # 执行命令
    def execute(self, command, src: CommandSource):
        if self.client is None or self.client.get_transport() is None:
            src.reply("请先使用!!ssh connect <地址> <用户名> <密码>进行连接")
        else:
            try:
                stdin, stdout, stderr = self.client.exec_command(command)
                output = stdout.read().decode().strip()
                error = stderr.read().decode().strip()
                if output:
                    src.reply(output)
                if error:
                    src.reply(error)
            except Exception as e:
                src.reply(f"执行命令失败: {e}")
                self.disconnect(src)

    # 断开连接
    def disconnect(self, src: CommandSource):
        if self.client is None or self.client.get_transport() is None:
            src.reply("尚未连接到任何SSH服务器")

        else:
            if self.client.get_transport().is_active():
                src.reply("警告：若有命令正在运行，强制断开会中断它们")
            self.client.close()
            self.client = None
            src.reply("已断开SSH连接")

def on_load(server: PluginServerInterface, old_module):
    ssh_client = SSHClient()

    server.register_command(
        Literal("!!ssh")
        .runs(lambda src: src.reply("使用!!ssh help查看帮助"))
        .then(Literal("connect")
              .then(Text("hostname")
                    .then(Text("username")
                          .then(Text("password")
                              .runs(lambda src, ctx: ssh_client.connect(ctx["hostname"], ctx["username"], ctx["password"], src))))))
        .then(Literal("disconnect")
              .runs(lambda src: ssh_client.disconnect(src)))
        .then(QuotableText("command")
              .runs(lambda src, ctx: ssh_client.execute(ctx["command"], src)))
    )

    server.logger.info("SSH客户端插件加载完成")
    
def on_unload(server: PluginServerInterface):
    ssh_client = SSHClient()
    ssh_client.disconnect(src)