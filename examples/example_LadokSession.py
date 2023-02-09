import ladok3
import weblogin.kth

ladok = ladok3.LadokSession(
        "KTH Royal Institute of Technology",
        autologin_handlers=[
          weblogin.kth.SAMLlogin(),
          weblogin.kth.UGlogin(os.environ["KTH_LOGIN"],
                               os.environ["KTH_PASSWD"])
        ],
        test_environment=True) # for experiments

