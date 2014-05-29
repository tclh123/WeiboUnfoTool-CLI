# coding=utf-8

from datetime import datetime

from weibounfo.client import client, owner_uid, APIError
from weibounfo.model.rule import Rule, Checker, Any, All, Not

from weibounfo.model.utils import weibo_date


def friends(uid, limit=None):
    users = []

    def f(cursor):
        r = client.friendships.friends.get(uid=uid, count=200, cursor=cursor,
                                           trim_status=0)
        return r

    r = f(cursor=0)
    users += r.users
    while r.next_cursor:
        if limit and limit < r.next_cursor:
            break

        r = f(r.next_cursor)
        users += r.users


    return users


class LastReportDateChecker(Checker):
    def check(self, user):
        if 'status' not in user:
            print '%s dont have status' % user.screen_name
            return True
        delta = datetime.now() - weibo_date(user.status.created_at)
        return delta.days > 365


class FollowersFriendsCountChecker(Checker):
    def check(self, user):
        return user.followers_count < 500 and user.friends_count > 1500


class StatusesCountChecker(Checker):
    def check(self, user):
        return user.statuses_count < 5


class FollowMeChecker(Checker):
    def check(self, user):
        return user.follow_me


class OnLineChecker(Checker):
    def check(self, user):
        return user.online_status == 1


class BiFollowersLow(Checker):
    def check(self, user):
        return user.bi_followers_count < 100


class BiFollowersHigh(Checker):
    def check(self, user):
        return user.bi_followers_count > 500


class JunkAccountRule(Rule):
    """ 垃圾号，通常是一些活跃度有问题的号 """
    pass


class LastReportSourceChecker(Checker):
    """ 最近一条微博的微博尾巴 """
    BANNED = [
            u"时光机",
            # u"皮皮时光机",
            u"未通过审核应用"
            ]
    def check(self, user):
        if 'status' not in user:
            # print '%s dont have status' % user.screen_name
            return True
        if 'source' not in user.status:
            print '%s last status deleted.' % user.screen_name
            return True

        for b in self.BANNED:
            if b in user.status.source:
                return True

        return False


class VerifiedChecker(Checker):
    """ 大 V """
    def check(self, user):
        return user.verified


class BigAccountChecker(Checker):
    def check(self, user):
        return user.followers_count > 200000 and user.statuses_count > 20000


class MarketingAccountRule(Rule):
    """ 营销号，大V """
    pass


def unfo(uid):
    r = client.friendships.destroy.post(uid=uid)
    if 'id' in r and r.id:
        return True
    return False


IS_PRINT = True
IS_DO_UNFO = True


def main():
    junkAccountRule = JunkAccountRule(
                        All(
                            Any(LastReportDateChecker(),
                                All(FollowersFriendsCountChecker(),
                                    BiFollowersLow()),
                                StatusesCountChecker()),
                            Not(FollowMeChecker()),
                            Not(OnLineChecker()),
                            Not(BiFollowersHigh())
                            )
                      )
    marketingAccountRule = MarketingAccountRule(
                All(LastReportSourceChecker(),
                    BigAccountChecker(),
                    Not(VerifiedChecker()))
            )
    users = friends(uid=owner_uid, limit=3000)
    users = filter(Any(junkAccountRule, marketingAccountRule).check, users)

    if IS_PRINT:
        for u in users:
            print u.screen_name

    if IS_DO_UNFO:
        max_retry = 5
        for u in users:
            r = None
            idx = 0
            while not r and idx < max_retry:
                try:
                    idx += 1
                    r = unfo(u.id)
                except APIError as e:
                    print repr(e)
                    print 'user_id: %s' % u.id


if __name__ == '__main__':
    main()
