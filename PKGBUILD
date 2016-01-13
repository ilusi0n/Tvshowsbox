pkgname=TVShowsBox
pkgver=0.1
pkgrel=1
pkgdesc='A script written in python that manages all your TV Shows in a sqlite database.'
arch=('any')
url="https://bitbucket.org/lanikai/tvshowsbox"
license=('GPL')
depends=('sqlite' 'python>=3.4')
source=("TVShowsBox.py")
install=${pkgname}.install

md5sums=('SKIP')

build() {
    cd "$srcdir"
}

package() {
    cd "$srcdir"
    install -Dm755 TVShowsBox.py "$pkgdir/usr/bin/TVShowsBox"
}
