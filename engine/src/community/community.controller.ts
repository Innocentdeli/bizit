import { Controller, Get, Post, Put, Body, Param, Req } from '@nestjs/common';
import { CommunityService } from './community.service';

@Controller('community')
export class CommunityController {
  constructor(private readonly communityService: CommunityService) {}

  @Get('channels')
  getChannels() {
    return this.communityService.getChannels();
  }

  @Post('channels')
  createChannel(@Body() body: { name: string; description: string; category: string; isPrivate?: boolean }) {
    return this.communityService.createChannel(body.name, body.description, body.category, body.isPrivate);
  }

  @Get('channels/:id/posts')
  getPosts(@Param('id') id: string) {
    return this.communityService.getPosts(id);
  }

  @Get('posts/:postId/comments')
  getComments(@Param('postId') postId: string) {
    return this.communityService.getComments(postId);
  }

  @Get('leaderboard')
  getLeaderboard() {
    return this.communityService.getLeaderboard();
  }

  @Get('profile/:userId')
  getProfile(@Param('userId') userId: string) {
    return this.communityService.getProfile(userId);
  }

  @Put('profile/:userId')
  updateProfile(@Param('userId') userId: string, @Body() body: { bio?: string; avatarUrl?: string }) {
    return this.communityService.updateProfile(userId, body.bio, body.avatarUrl);
  }

  @Get('events')
  getEvents() {
    return this.communityService.getEvents();
  }

  @Post('events')
  createEvent(@Body() body: { organizerId: string; title: string; description: string; date: string; location?: string }) {
    return this.communityService.createEvent(body.organizerId, body.title, body.description, body.date, body.location);
  }

  @Post('events/:eventId/attend')
  attendEvent(@Param('eventId') eventId: string, @Body('userId') userId: string) {
    return this.communityService.attendEvent(eventId, userId);
  }

  @Post('mentorship/request')
  requestMentorship(@Body() body: { mentorId: string; menteeId: string }) {
    return this.communityService.requestMentorship(body.mentorId, body.menteeId);
  }

  @Put('mentorship/:id/status')
  updateMentorshipStatus(@Param('id') id: string, @Body('status') status: string) {
    return this.communityService.updateMentorshipStatus(id, status);
  }

  @Get('search')
  search(@Req() req: any) {
    return this.communityService.search(req.query.q as string || '');
  }

  @Get('notifications/:userId')
  getNotifications(@Param('userId') userId: string) {
    return this.communityService.getNotifications(userId);
  }

  @Post('notifications/:userId/read')
  markNotificationsRead(@Param('userId') userId: string) {
    return this.communityService.markNotificationsRead(userId);
  }

  @Post('posts/:id/delete')
  deletePost(@Param('id') id: string, @Body('userId') userId: string) {
    return this.communityService.deletePost(id, userId);
  }
}
