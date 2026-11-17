using System;
using System.Drawing;
using System.Windows.Forms;

static class Program
{
    [STAThread]
    static void Main()
    {
        Application.EnableVisualStyles();
        Application.Run(new LoginForm());
    }
}

public class LoginForm : Form
{
    public LoginForm()
    {
        Text = "UIDemo Login";
        AccessibleName = "UIDemo Login";
        Size = new Size(440, 230);
        FormBorderStyle = FormBorderStyle.FixedDialog;
        StartPosition = FormStartPosition.CenterScreen;
        MaximizeBox = false;

        var lblUser = new Label { Text = "Username", Location = new Point(20, 25), Size = new Size(90, 23) };
        var edUsername = new TextBox { Name = "edUsername", AccessibleName = "edUsername", Location = new Point(120, 22), Size = new Size(280, 23) };
        var lblPass = new Label { Text = "Password", Location = new Point(20, 65), Size = new Size(90, 23) };
        var edPassword = new TextBox { Name = "edPassword", AccessibleName = "edPassword", Location = new Point(120, 62), Size = new Size(280, 23), PasswordChar = '*' };
        var btnLogIn = new Button { Name = "btnLogIn", AccessibleName = "btnLogIn", Text = "Log In", Location = new Point(120, 105), Size = new Size(120, 32) };
        var lblMsg = new Label { Name = "lblMsg", Text = "", Location = new Point(20, 150), Size = new Size(380, 25), ForeColor = Color.Red };

        btnLogIn.Click += (s, e) =>
        {
            if (edUsername.Text == "admin" && edPassword.Text == "password")
            {
                Hide();
                new UiDemoForm(this).Show();
            }
            else
            {
                lblMsg.Text = "Wrong login or password";
            }
        };

        Controls.AddRange(new Control[] { lblUser, edUsername, lblPass, edPassword, btnLogIn, lblMsg });
        AcceptButton = btnLogIn;
    }
}

public class UiDemoForm : Form
{
    private readonly TextBox edCashIn = new TextBox();
    private readonly TextBox edOnUsCheck = new TextBox();
    private readonly TextBox edNotOnUsCheck = new TextBox();
    private readonly ListBox listAccepted = new ListBox();
    private readonly Form login;

    public UiDemoForm(Form login)
    {
        this.login = login;
        Text = "UiDemo";
        AccessibleName = "UiDemo";
        Size = new Size(540, 460);
        StartPosition = FormStartPosition.CenterScreen;

        var lblSuccess = new Label { Name = "UIDemo_LoginSuccess", AccessibleName = "UIDemo_LoginSuccess", Text = "UIDemo_LoginSuccess", Location = new Point(400, 18), AutoSize = true };

        var lbl1 = new Label { Text = "Cash In", Location = new Point(20, 23), Size = new Size(120, 23) };
        edCashIn.Name = "edCashIn"; edCashIn.AccessibleName = "edCashIn";
        edCashIn.Location = new Point(150, 20); edCashIn.Size = new Size(160, 23);

        var lbl2 = new Label { Text = "On Us Check", Location = new Point(20, 58), Size = new Size(120, 23) };
        edOnUsCheck.Name = "edOnUsCheck"; edOnUsCheck.AccessibleName = "edOnUsCheck";
        edOnUsCheck.Location = new Point(150, 55); edOnUsCheck.Size = new Size(160, 23);

        var lbl3 = new Label { Text = "Not On Us Check", Location = new Point(20, 93), Size = new Size(125, 23) };
        edNotOnUsCheck.Name = "edNotOnUsCheck"; edNotOnUsCheck.AccessibleName = "edNotOnUsCheck";
        edNotOnUsCheck.Location = new Point(150, 90); edNotOnUsCheck.Size = new Size(160, 23);

        var btnAccept = new Button { Name = "btnAccept", AccessibleName = "btnAccept", Text = "Accept", Location = new Point(150, 130), Size = new Size(120, 32) };
        var lblAccepted = new Label { Text = "Accepted transactions:", Location = new Point(20, 180), AutoSize = true };

        listAccepted.Location = new Point(20, 205);
        listAccepted.Size = new Size(490, 180);

        btnAccept.Click += (s, e) =>
        {
            decimal a, b, c;
            if (decimal.TryParse(edCashIn.Text, out a) && decimal.TryParse(edOnUsCheck.Text, out b) && decimal.TryParse(edNotOnUsCheck.Text, out c))
            {
                listAccepted.Items.Add(string.Format("CashIn={0}; OnUsCheck={1}; NotOnUsCheck={2}", a, b, c));
                edCashIn.Text = "";
                edOnUsCheck.Text = "";
                edNotOnUsCheck.Text = "";
            }
            else
            {
                MessageBox.Show(this, "Значения не числовые", "UIDemo", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        };

        FormClosing += (s, e) =>
        {
            if (e.CloseReason == CloseReason.UserClosing)
            {
                e.Cancel = true;
                Application.Exit();
            }
        };

        Controls.AddRange(new Control[]
        {
            lblSuccess, lbl1, edCashIn, lbl2, edOnUsCheck, lbl3, edNotOnUsCheck, btnAccept, lblAccepted, listAccepted
        });
    }
}
