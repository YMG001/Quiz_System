import sys
import pkg_resources

def check_environment():
    print(f"Python 版本: {sys.version}")
    print("\n已安装的包:")
    for pkg in pkg_resources.working_set:
        print(f"{pkg.key} == {pkg.version}")

if __name__ == "__main__":
    check_environment() 