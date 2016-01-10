pkgname=TVShowsBox
pkgver=0.1
pkgrel=1
pkgdesc='A script written in python that manages all your TV Shows in a sqlite database.'
arch=('any')
url="https://bitbucket.org/lanikai/tvshowsbox"
license=('GPL')
depends=('sqlite' 'python>=3.4')
source=("TVShowsBox.py")

md5sums=('4ad5337338eeff9f0e0429c151faaad6'
         'ded9fa8a6f295d34b11e852c1cd48062'
         'b1b74c67e04ea5ca142075e8256f562f')

build() {
    cd "$srcdir"
}

package() {
    cd "$srcdir"
    install -Dm755 TVShowsBox.py "$pkgdir/usr/bin/TVShowsBox"
}