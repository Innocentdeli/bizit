import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '../prisma.service';

@Injectable()
export class CommunityService {
  private readonly logger = new Logger(CommunityService.name);

  constructor(private prisma: PrismaService) {}

  async getChannels() {
    return this.prisma.communityChannel.findMany({
      orderBy: { createdAt: 'asc' },
    });
  }

  async createChannel(name: string, description: string, category: string, isPrivate: boolean = false) {
    return this.prisma.communityChannel.create({
      data: { name, description, category, isPrivate },
    });
  }

  async getPosts(channelId: string) {
    return this.prisma.communityPost.findMany({
      where: { channelId },
      include: {
        author: {
          select: { id: true, firstName: true, lastName: true, email: true }
        },
        reactions: true,
        _count: { select: { comments: true } }
      },
      orderBy: { createdAt: 'desc' },
      take: 50,
    });
  }

  async createPost(channelId: string, authorId: string, content: string) {
    // Ensure author exists, fallback if not
    const userExists = await this.prisma.user.findUnique({ where: { id: authorId } });
    if (!userExists) {
      await this.prisma.user.create({
        data: {
          id: authorId,
          email: `${authorId}@example.com`,
          firstName: "Unknown",
          lastName: "User",
        }
      });
    }

    const post = await this.prisma.communityPost.create({
      data: {
        channelId,
        authorId,
        content,
      },
      include: {
        author: {
          select: { id: true, firstName: true, lastName: true, email: true }
        },
        reactions: true,
        _count: { select: { comments: true } }
      }
    });

    // Add 10 XP for posting
    await this.addXp(authorId, 10);
    return post;
  }

  async getComments(postId: string) {
    return this.prisma.communityComment.findMany({
      where: { postId },
      include: {
        author: {
          select: { id: true, firstName: true, lastName: true, email: true }
        },
        reactions: true,
      },
      orderBy: { createdAt: 'asc' }
    });
  }

  async createComment(postId: string, authorId: string, content: string) {
    const comment = await this.prisma.communityComment.create({
      data: { postId, authorId, content },
      include: {
        author: {
          select: { id: true, firstName: true, lastName: true, email: true }
        },
        reactions: true,
      }
    });

    // Notify post author if different from commenter
    const post = await this.prisma.communityPost.findUnique({ where: { id: postId } });
    if (post && post.authorId !== authorId) {
      const commenter = await this.prisma.user.findUnique({ where: { id: authorId }, select: { firstName: true, lastName: true } });
      const name = commenter ? `${commenter.firstName} ${commenter.lastName}`.trim() : 'Someone';
      await this.createNotification(post.authorId, 'reply', `${name} replied to your post`, `/community/posts/${postId}`);
    }

    await this.addXp(authorId, 5); // 5 XP for commenting
    return comment;
  }

  async addReaction(postId: string, authorId: string, emoji: string) {
    // Basic implementation (upsert behavior to avoid duplicate unique error logic)
    const existing = await this.prisma.communityReaction.findFirst({
      where: { postId, authorId, emoji }
    });

    if (!existing) {
      const reaction = await this.prisma.communityReaction.create({
        data: { postId, authorId, emoji }
      });

      // Notify post author if different from reactor
      const post = await this.prisma.communityPost.findUnique({ where: { id: postId } });
      if (post && post.authorId !== authorId) {
        const reactor = await this.prisma.user.findUnique({ where: { id: authorId }, select: { firstName: true, lastName: true } });
        const name = reactor ? `${reactor.firstName} ${reactor.lastName}`.trim() : 'Someone';
        await this.createNotification(post.authorId, 'reaction', `${name} reacted ${emoji} to your post`);
      }

      return { action: 'added', reaction };
    } else {
      await this.prisma.communityReaction.delete({ where: { id: existing.id } });
      return { action: 'removed', reaction: existing };
    }
  }

  async getLeaderboard() {
    return this.prisma.communityProfile.findMany({
      orderBy: { xp: 'desc' },
      take: 10,
      include: {
        user: { select: { firstName: true, lastName: true } }
      }
    });
  }

  async getProfile(userId: string) {
    let profile = await this.prisma.communityProfile.findUnique({
      where: { userId },
      include: { user: true }
    });
    if (!profile) {
      profile = await this.prisma.communityProfile.create({
        data: { userId },
        include: { user: true }
      });
    }
    return profile;
  }

  async updateProfile(userId: string, bio?: string, avatarUrl?: string) {
    await this.getProfile(userId);
    return this.prisma.communityProfile.update({
      where: { userId },
      data: { bio, avatarUrl },
      include: { user: true }
    });
  }

  async getEvents() {
    return this.prisma.communityEvent.findMany({
      include: {
        organizer: { select: { firstName: true, lastName: true } },
        _count: { select: { attendees: true } }
      },
      orderBy: { date: 'asc' }
    });
  }

  async createEvent(organizerId: string, title: string, description: string, date: string, location?: string) {
    return this.prisma.communityEvent.create({
      data: { organizerId, title, description, date: new Date(date), location }
    });
  }

  async attendEvent(eventId: string, userId: string) {
    const userExists = await this.prisma.user.findUnique({ where: { id: userId } });
    if (!userExists) {
      await this.prisma.user.create({
        data: { id: userId, email: `${userId}@example.com`, firstName: 'Unknown', lastName: 'User' }
      });
    }
    try {
      return await this.prisma.communityEventAttendee.create({ data: { eventId, userId } });
    } catch (e) {
      return null;
    }
  }

  async requestMentorship(mentorUserId: string, menteeUserId: string) {
    const mentorProfile = await this.getProfile(mentorUserId);
    const menteeProfile = await this.getProfile(menteeUserId);

    const mentorship = await this.prisma.mentorship.create({
      data: { mentorId: mentorProfile.id, menteeId: menteeProfile.id, status: 'pending' }
    });

    // Notify the mentor
    const mentee = await this.prisma.user.findUnique({ where: { id: menteeUserId }, select: { firstName: true, lastName: true } });
    const name = mentee ? `${mentee.firstName} ${mentee.lastName}`.trim() : 'Someone';
    await this.createNotification(mentorUserId, 'mentorship_request', `${name} sent you a mentorship request`);

    return mentorship;
  }

  async updateMentorshipStatus(mentorshipId: string, status: string) {
    return this.prisma.mentorship.update({ where: { id: mentorshipId }, data: { status } });
  }

  async search(query: string) {
    const posts = await this.prisma.communityPost.findMany({
      where: { content: { contains: query, mode: 'insensitive' } },
      include: {
        author: { select: { firstName: true, lastName: true } },
        channel: { select: { name: true, id: true } }
      },
      take: 10
    });
    const channels = await this.prisma.communityChannel.findMany({
      where: { name: { contains: query, mode: 'insensitive' } },
      take: 5
    });
    return { posts, channels };
  }

  async getNotifications(userId: string) {
    return this.prisma.notification.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' },
      take: 20
    });
  }

  async markNotificationsRead(userId: string) {
    return this.prisma.notification.updateMany({
      where: { userId, isRead: false },
      data: { isRead: true }
    });
  }

  async deletePost(postId: string, userId: string) {
    const profile = await this.getProfile(userId);
    const post = await this.prisma.communityPost.findUnique({ where: { id: postId } });
    if (!post) throw new Error('Post not found');
    if (post.authorId !== profile.id && profile.role !== 'MODERATOR' && profile.role !== 'ADMIN') {
      throw new Error('Unauthorized to delete this post');
    }
    return this.prisma.communityPost.delete({ where: { id: postId } });
  }

  private async createNotification(userId: string, type: string, message: string, link?: string) {
    try {
      return await this.prisma.notification.create({
        data: { userId, type, message, link }
      });
    } catch (e) {
      this.logger.warn(`Could not create notification for ${userId}: ${e}`);
      return null;
    }
  }

  private async addXp(userId: string, amount: number) {
    const profile = await this.getProfile(userId);
    const newXp = profile.xp + amount;
    const newLevel = Math.floor(newXp / 100) + 1;
    await this.prisma.communityProfile.update({
      where: { userId },
      data: { xp: newXp, level: newLevel }
    });
  }
}
