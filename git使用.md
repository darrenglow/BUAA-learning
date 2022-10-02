比较简略的记录一下

主要是为了上传github方便

省略了前面的git下载，ssh连接的步骤了，只记录上传的操作。

步骤：

1. 在本地新建文件夹
2. 右键，GIT BASH HERE
3. `git init`
4. 此时就可以把想要上传的文件放进去了
5. `git add .`
6. `git commit -m "输入注释"`
7. 此时需要连接github的仓库

`git remote add origin https://github.com/darrenglow/BUAA-learning.git`

8. 连接后就可以push了，`git push -u origin master`，第一次加上-u即可，后面可省略了
9. 这样就上传成功了。