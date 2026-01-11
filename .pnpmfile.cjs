function readPackage(pkg, context) {
  // 修改包的配置
  return pkg;
}

module.exports = {
  hooks: {
    readPackage
  }
};