import {
  WebSocketGateway,
  WebSocketServer,
  SubscribeMessage,
  MessageBody,
  ConnectedSocket,
  OnGatewayConnection,
  OnGatewayDisconnect,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { CommunityService } from './community.service';
import { Logger } from '@nestjs/common';

@WebSocketGateway({
  cors: {
    origin: '*',
  },
})
export class CommunityGateway implements OnGatewayConnection, OnGatewayDisconnect {
  @WebSocketServer()
  server: Server;

  private readonly logger = new Logger(CommunityGateway.name);

  constructor(private readonly communityService: CommunityService) {}

  handleConnection(client: Socket) {
    this.logger.log(`Client connected: ${client.id}`);
  }

  handleDisconnect(client: Socket) {
    this.logger.log(`Client disconnected: ${client.id}`);
  }

  /** Client calls this right after connecting with their Clerk userId */
  @SubscribeMessage('registerUser')
  handleRegisterUser(@ConnectedSocket() client: Socket, @MessageBody() userId: string) {
    client.join(`user:${userId}`);
    this.logger.log(`Client ${client.id} registered as user: ${userId}`);
    return { event: 'registered', data: userId };
  }

  @SubscribeMessage('joinChannel')
  handleJoinChannel(@ConnectedSocket() client: Socket, @MessageBody() channelId: string) {
    client.join(channelId);
    this.logger.log(`Client ${client.id} joined channel: ${channelId}`);
    return { event: 'joined', data: channelId };
  }

  @SubscribeMessage('leaveChannel')
  handleLeaveChannel(@ConnectedSocket() client: Socket, @MessageBody() channelId: string) {
    client.leave(channelId);
    this.logger.log(`Client ${client.id} left channel: ${channelId}`);
  }

  @SubscribeMessage('sendMessage')
  async handleSendMessage(
    @ConnectedSocket() client: Socket,
    @MessageBody() payload: { channelId: string; authorId: string; content: string },
  ) {
    const post = await this.communityService.createPost(payload.channelId, payload.authorId, payload.content);
    this.server.to(payload.channelId).emit('newMessage', post);
    return post;
  }

  @SubscribeMessage('sendComment')
  async handleSendComment(
    @ConnectedSocket() client: Socket,
    @MessageBody() payload: { postId: string; authorId: string; content: string; channelId: string },
  ) {
    const comment = await this.communityService.createComment(payload.postId, payload.authorId, payload.content);
    this.server.to(payload.channelId).emit('newComment', { ...comment, postId: payload.postId });

    // Push a live notification to the post author's room
    const notif = await this.communityService.getNotifications(payload.authorId);
    if (notif.length > 0) {
      this.server.to(`user:${payload.authorId}`).emit('notification', notif[0]);
    }

    return comment;
  }

  @SubscribeMessage('addReaction')
  async handleAddReaction(
    @ConnectedSocket() client: Socket,
    @MessageBody() payload: { postId: string; authorId: string; emoji: string; channelId: string },
  ) {
    const result = await this.communityService.addReaction(payload.postId, payload.authorId, payload.emoji);
    this.server.to(payload.channelId).emit('reactionUpdated', {
      postId: payload.postId,
      authorId: payload.authorId,
      emoji: payload.emoji,
      action: result.action,
    });
    return result;
  }
}
